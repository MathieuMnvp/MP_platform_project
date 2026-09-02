from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import shutil
import math
import logging

import numpy as np
import pandas as pd

from Neutronics.NeInputGenerator import NeInputGenerator
from Neutronics.NeOutputReader import NeOutputReader
from Thermohydraulics.ThInputGenerator import ThInputGenerator
from Thermohydraulics.ThOutputReader import ThOutputReader
from Utils.JSON_server import JSON_server
from Utils.json_utils import json_reader

__all__ = ["GaussSeidel"]

logger = logging.getLogger(__name__)

CONFIG_FILENAME = "config.json"
CONVERGENCE_FILENAME = "convergence.csv"
CONVERGENCE_THRESHOLD = 1.0 #pas très élégant que tous les critères n'utilisent pas cette valeur (norme L2 notamment)
MARGIN_FACTOR = 1.05

@dataclass
class GaussSeidel:
    casename: str = "default"
    scenario: str = "default"
    thermo_code: str = "default"
    neutro_code: str = "default"
    iteration: int = 1
    start_iteration: int = 1
    last_iteration: int = 1

    ne_input: NeInputGenerator = field(default_factory=NeInputGenerator)
    ne_output: NeOutputReader = field(default_factory=NeOutputReader)
    th_input: ThInputGenerator = field(default_factory=ThInputGenerator)
    th_output: ThOutputReader = field(default_factory=ThOutputReader)
    JSserv: JSON_server = field(default_factory=JSON_server)
    
    def __post_init__(self) -> None:
        if self.last_iteration <= 0:
            raise ValueError("last_iteration doit être > 0")
        if self.start_iteration <= 0:
            raise ValueError("start_iteration doit être > 0")
        if self.start_iteration > self.last_iteration:
            raise ValueError(
                f"start_iteration ({self.start_iteration}) doit être "
                f"<= last_iteration ({self.last_iteration})"
            )  

    @property
    def scenario_dir(self) -> Path:
        return Path.cwd() / "Scenarios" / self.scenario
    
    @property
    def results_dir(self) -> Path:
        return Path.cwd() / "Results" / self.casename

    @property
    def config_path(self) -> Path:
        return self.scenario_dir / CONFIG_FILENAME

    @property
    def convergence_path(self) -> Path:
        return self.results_dir / CONVERGENCE_FILENAME

    # ------------------------------------------------------------------
    # main
    # ----------------------------------------------------------------

    def main(self, restart: bool = False) -> None:
        self._apply_config()

        first_iteration=self.start_iteration
        if restart:
            first_iteration = self._resume()

        logger.info(
            "Couplage Gauss-Seidel : itérations %d → %d (case=%s, scenario=%s)",
            first_iteration, self.last_iteration, self.casename, self.scenario,
        )

        for iteration in range(first_iteration, self.last_iteration + 1):
            self._run_iteration(iteration)

            if iteration > first_iteration and self._has_converged(iteration):
                logger.info("Convergence atteinte à l'itération %d", iteration)
                return

        

        logger.warning(
            "Pas de convergence après %d itérations", self.last_iteration
        )

    # ------------------------------------------------------------------
    # Couplage
    # ------------------------------------------------------------------            

    def _run_iteration(self, iteration: int) -> None:
        """Un pas Gauss-Seidel : thermohydraulique puis neutronique. -> pas sur, vérifier, en plus ca m'arrange pas"""
        logger.info("--- Itération %d ---", iteration)
        self.JSserv.start()
        try:
            self.JSserv.json_server("iteration", int(iteration))
            self._run_neutronics(iteration)
            self._run_thermohydraulics(iteration)
        finally:
            self.JSserv.stop()

    def _run_neutronics(self, iteration: int) -> None:
        self.JSserv.json_server("physics", "neutronics")
        for module in (self.ne_input, self.ne_output):
            self._configure(module, iteration, neutro_code=self.neutro_code)
            module.main()

    def _run_thermohydraulics(self, iteration: int) -> None:
        self.JSserv.json_server("physics", "thermohydraulics")
        for module in (self.th_input, self.th_output):
            self._configure(module, iteration, thermo_code=self.thermo_code)
            module.main()

    def _configure(self, module, iteration: int, **extra) -> None:
        """Propage l'état du couplage vers un sous-module."""
        module.casename = self.casename
        module.scenario = self.scenario
        module.iteration = iteration
        for key, value in extra.items():
            setattr(module, key, value)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
        
    def _apply_config(self) -> None:
        config = self._load_config()
        self.neutro_code = config["neutronics"]
        self.thermo_code = config["thermohydraulics"]

        coupling_cfg = config["coupling_dependant"]
        self.last_iteration = coupling_cfg["total_iteration"]
        self.start_iteration = coupling_cfg["starting_iteration"]
        self._validate_iterations()

        self.JSserv.json_server("neutronics", self.neutro_code)
        self.JSserv.json_server("thermohydraulics", self.thermo_code)

    def _load_config(self) -> dict:
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Config introuvable : {self.config_path}")
        return json_reader(str(self.config_path))

    def _validate_iterations(self) -> None:
        if self.start_iteration <= 0:
            raise ValueError("start_iteration doit être > 0")
        if self.last_iteration <= 0:
            raise ValueError("last_iteration doit être > 0")
        if self.start_iteration > self.last_iteration:
            raise ValueError(
                f"start_iteration ({self.start_iteration}) doit être <= "
                f"last_iteration ({self.last_iteration})")

    # ------------------------------------------------------------------
    # Convergence
    # ------------------------------------------------------------------

    def _has_converged(self, iteration: int) -> bool:
        keff_converged = self._check_keff_convergence(iteration)
        spatial_converged = self._check_spatial_convergence(iteration)
    
        return keff_converged and spatial_converged       

    def _check_keff_convergence(self, iteration:int) -> bool:
        if not self.convergence_path.is_file():
            logger.debug("Pas encore de fichier de résidus")
            return False

        data = pd.read_csv(self.convergence_path)
        if len(data) < 2:
            return False

        keff_old, keff_new = data["keff"].tail(2).to_numpy()
        sigma_old, sigma_new = data["sigma_keff"].tail(2).to_numpy()

        sigma_combined = math.hypot(sigma_new, sigma_old)
        if sigma_combined == 0.0:
            logger.warning("sigma_keff nul : convergence non évaluable")
            return False

        residual = abs(keff_new - keff_old) / sigma_combined
        logger.info("Itération %d — résidu keff = %.3f (seuil = %.1f)",
                    iteration, residual, CONVERGENCE_THRESHOLD)

        self._record_residual(data, residual)
        return residual <= CONVERGENCE_THRESHOLD * MARGIN_FACTOR

    def _check_spatial_convergence(self, iteration:int) -> bool:
        if not self.convergence_path.is_file():
            logger.debug("Pas encore de fichier de convergence")
            return False

        data = pd.read_csv(self.convergence_path)
        if len(data) < 2:
            return False

        new_power = pd.read_csv(self.results_dir / str(iteration) / "NE_output.csv")
        old_power = pd.read_csv(self.results_dir / str(iteration-1) / "NE_output.csv")

        power_new = new_power["Power"].to_numpy()
        power_std_dev_new = new_power["Power_Std_Dev"].to_numpy()

        power_old = old_power["Power"].to_numpy()
        power_std_dev_old = old_power["Power_Std_Dev"].to_numpy()

        L2_norm_power = np.linalg.norm(power_new-power_old)
        minimal_L2_norm_possible = np.sqrt(np.sum(power_std_dev_new**2 + power_std_dev_old**2))

        self._record_L2_norm(data, L2_norm_power/minimal_L2_norm_possible)
        return L2_norm_power <= minimal_L2_norm_possible * MARGIN_FACTOR

    def _record_L2_norm(self, data: pd.DataFrame, L2_norm_power: float, L2_norm_power_std_dev: float) -> None:
        if "Power_L2" not in data.columns:
            data["Power_L2"] = pd.NA
        data.loc[data.index[-1], "Power_L2"] = L2_norm_power
        data.to_csv(self.convergence_path, index=False, float_format="%.6f")

    def _record_residual(self, data: pd.DataFrame, residual: float) -> None:
        if "keff_residual" not in data.columns:
            data["keff_residual"] = pd.NA
        data.loc[data.index[-1], "keff_residual"] = residual
        data.to_csv(self.convergence_path, index=False, float_format="%.6f")

    # ------------------------------------------------------------------
    # Restart
    # ------------------------------------------------------------------

    def _resume(self) -> int:
        latest = self._latest_completed_iteration()

        if latest is None:
            raise FileNotFoundError(
                f"Impossible de redémarrer : aucun résultat dans "
                f"'{self.results_dir}'"
            )
        logger.info("Reprise détectée à l'itération %d", latest)

        self.JSserv.start()
        try:
            iteration_dir = self.results_dir / str(latest)
            self.JSserv.json_server("iteration", int(latest))
            if (iteration_dir / "NE_output.csv").is_file(): 
                shutil.rmtree(iteration_dir / "Thermohydraulics", ignore_errors=True)
                self._run_thermohydraulics(latest)
            else:
                shutil.rmtree(iteration_dir / "Neutronics", ignore_errors=True)
                self._run_neutronics(latest)
                self._run_thermohydraulics(latest)
        finally:
            self.JSserv.stop()

        return latest + 1

    def _latest_completed_iteration(self) -> int | None:
        if not self.results_dir.is_dir():
            return None
        iterations = [
            int(p.name) for p in self.results_dir.iterdir()
            if p.is_dir() and p.name.isdigit()
        ]
        return max(iterations, default=None)

