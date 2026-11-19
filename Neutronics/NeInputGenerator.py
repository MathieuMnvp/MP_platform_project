from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from Neutronics.openmc.OpenMcInputGenerator import OpenMcInputGenerator
from Utils.json_utils import json_reader

__all__ = ["NeInputGenerator"]

logger = logging.getLogger(__name__)

CONFIG_FILENAME = "config.json"

@dataclass
class NeInputGenerator:
    iteration: int = 0
    casename: str = "default"
    scenario: str = "default"
    neutro_code: str = "default"

    openmc_input: OpenMcInputGenerator = field(default_factory=OpenMcInputGenerator)

    @property
    def scenario_dir(self) -> Path:
        return Path.cwd() / "Scenarios" / self.scenario

    @property
    def config_path(self) -> Path:
        return self.scenario_dir / CONFIG_FILENAME

    def main(self) -> None:
        readers = {
            "openmc": self._run_openmc,
        }
        try:
            read = readers[self.neutro_code]
        except KeyError:
            raise ValueError(
                f"Code neutronique non supporté : {self.neutro_code!r} "
                f"(supportés : {', '.join(readers)})"
            ) from None

        logger.info("Simulation neutronique %s (itération %d)",
                    self.neutro_code, self.iteration)
        read()

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Config introuvable : {self.config_path}")
        return json_reader(str(self.config_path))

    def _run_openmc(self) -> None:
        settings = self._load_config()["openmc"]

        self.openmc_input.batches = settings["batches"]
        self.openmc_input.inactive = settings["inactive"]
        self.openmc_input.scenario = self.scenario
        self.openmc_input.casename = self.casename
        self.openmc_input.iteration = self.iteration
        self.openmc_input.main()