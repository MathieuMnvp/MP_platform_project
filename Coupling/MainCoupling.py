import logging
from pathlib import Path
from dataclasses import dataclass

from Coupling.GaussSeidel import GaussSeidel
from Utils.json_utils import json_reader

__all__ = ["MainCoupling"]

logger = logging.getLogger(__name__)

CONFIG_FILENAME = "config.json"

COUPLING_METHODS = {
    "GaussSeidel": GaussSeidel,
}


@dataclass
class MainCoupling:
    casename: str = "default"
    scenario: str = "default"

    @property
    def scenario_dir(self) -> Path:
        return Path.cwd() / "Scenarios" / self.scenario

    @property
    def config_path(self) -> Path:
        return self.scenario_dir / CONFIG_FILENAME

    def main(self, restart: bool = False) -> None:
        config = self._load_config()
        method_name = config["coupling"]
        logger.info("Démarrage couplage '%s' (scenario=%s, case=%s)",
                    method_name, self.scenario, self.casename)
        solver = self._build_solver(method_name)
        solver.main(restart)

    def _load_config(self) -> dict:
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Config introuvable : {self.config_path}")
        return json_reader(str(self.config_path))

    def _build_solver(self, method_name: str):
        try:
            solver_cls = COUPLING_METHODS[method_name]
        except KeyError:
            available = ", ".join(COUPLING_METHODS)
            raise ValueError(
                f"Méthode de couplage inconnue : '{method_name}'. "
                f"Disponibles : {available}"
            )
        solver = solver_cls()
        solver.casename = self.casename
        solver.scenario = self.scenario
        return solver
