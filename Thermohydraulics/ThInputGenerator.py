from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from Thermohydraulics.openfoam.OpenFOAMInputGenerator import OpenFOAMInputGenerator

__all__ = ["ThInputGenerator"]

logger = logging.getLogger(__name__)

CONFIG_FILENAME = "config.json"

@dataclass
class ThInputGenerator:
    iteration: int = 0
    casename: str = "default"
    scenario: str = "default"
    thermo_code: str = "default"

    openfoam_input: OpenFOAMInputGenerator = field(default_factory=OpenFOAMInputGenerator)

    @property
    def results_dir(self) -> Path:
        return Path.cwd() / "Results" / self.casename / str(self.iteration) / "Thermohydraulics"

    @property
    def scenario_dir(self) -> Path:
        return Path.cwd() / "Scenarios" / self.scenario   

    def main(self) -> None:
        readers = {
            "openmc": self._run_openfoam,
        }
        try:
            read = readers[self.thermo_code]
        except KeyError:
            raise ValueError(
                f"Code thermohydraulique non supporté : {self.thermo_code!r} "
                f"(supportés : {', '.join(readers)})"
            ) from None

        logger.info("Simulation thermohydraulique %s (itération %d)",
                    self.thermo_code, self.iteration)
        read()

    def _run_openfoam(self) -> None:
            self.openfoam_input.scenario = self.scenario
            self.openfoam_input.casename = self.casename
            self.openfoam_input.iteration = self.iteration
            self.openfoam_input.main()