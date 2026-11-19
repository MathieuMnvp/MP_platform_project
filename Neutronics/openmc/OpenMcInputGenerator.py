from __future__ import annotations

import importlib.util
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import openmc

__all__ = ["OpenMcInputGenerator"]

logger = logging.getLogger(__name__)

SCENARIO_CLASS_NAME = "OpenMCInput"
REQUIRED_XML = ("settings.xml", "geometry.xml", "materials.xml")
OPENMC_LOG_FILENAME = "openmc.log"

@dataclass
class OpenMcInputGenerator:
    processors: int = 0
    iteration: int = 0
    batches: int = 0
    inactive: int = 0
    casename: str = "default"
    scenario: str = "default"

    @property
    def scenario_dir(self) -> Path:
        return Path.cwd() / "Scenarios" / self.scenario

    @property
    def scenario_script(self) -> Path:
        return self.scenario_dir / "openmc" / f"{self.scenario}_openmc.py"

    @property
    def results_dir(self) -> Path:
        return Path.cwd() / "Results" / self.casename / str(self.iteration) / "Neutronics"

    @property
    def n_threads(self) -> int:
        return self.processors if self.processors > 0 else (os.cpu_count() or 1)

    def main(self) -> None:
        logger.info("Lancement du calcul OpenMC (itération %d)", self.iteration)
        self._reset_ids()
        self._generate_inputs()
        self._run_simulation()

    def _reset_ids(self) -> None:
        for cls in (openmc.Cell, openmc.Material, openmc.Surface,
                    openmc.Universe, openmc.Tally, openmc.Filter):
            cls.used_ids.clear()
        openmc.reset_auto_ids()

    def _load_class_from_file(self, filepath: Path, class_name: str) -> type:
        if not filepath.is_file():
            raise FileNotFoundError(f"Script de scénario introuvable : {filepath}")

        module_name = f"scenario_{filepath.stem}"
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec is None or spec.loader is None:
            raise ImportError(f"Impossible de charger le module : {filepath}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module  # requis pour les dataclasses du script
        spec.loader.exec_module(module)

        try:
            return getattr(module, class_name)
        except AttributeError:
            raise AttributeError(
                f"Le script {filepath.name} doit définir une classe {class_name!r}"
            ) from None

    def _generate_inputs(self) -> None:
        input_cls = self._load_class_from_file(self.scenario_script, SCENARIO_CLASS_NAME)

        model = input_cls()
        model.batches = self.batches
        model.inactive = self.inactive
        model.iteration = self.iteration
        model.casename = self.casename
        model.main()

        missing = [f for f in REQUIRED_XML if not (self.results_dir / f).is_file()]
        if missing:
            raise FileNotFoundError(
                f"Le script de scénario n'a pas produit {', '.join(missing)} "
                f"dans {self.results_dir}"
            )

    def _run_simulation(self) -> None:
        logger.info("OpenMC : %d threads (itération %d)", self.n_threads, self.iteration)

        start = time.perf_counter()
        with subprocess.Popen(
            ["openmc", "--threads", str(self.n_threads)],
            cwd=self.results_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,   # stderr fusionné dans stdout
            text=True,
            bufsize=1,
        ) as proc:
            for line in proc.stdout:
                logger.info(line.rstrip())   # rstrip : retire le \n final

        if proc.returncode != 0:
            logger.error("OpenMC a échoué (code %d)", proc.returncode)
            raise RuntimeError(f"OpenMC a échoué (code {proc.returncode})")

        elapsed = time.perf_counter() - start
        logger.info("Calcul OpenMC terminé en %.0f s (itération %d)", elapsed, self.iteration)