from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from Thermohydraulics.openfoam.OpenFOAMOutputReader import OpenFOAMOutputReader

__all__ = ["ThOutputReader"]

logger = logging.getLogger(__name__)

CONFIG_FILENAME = "config.json"

@dataclass
class ThOutputReader:
    iteration: int = 0
    casename: str = "default"
    scenario: str = "default"
    thermo_code: str = "default"

    opemfoam_output: OpenFOAMOutputReader = field(default_factory=OpenFOAMOutputReader)

    @property
    def scenario_dir(self) -> Path:
        return Path.cwd() / "Scenarios" / self.scenario

    @property
    def results_dir(self):
        return Path.cwd() / "Results" / self.casename / str(self.iteration) / "Thermohydraulics"
    
    @property
    def output_dir(self):
        return Path.cwd() / "Results" / self.casename / str(self.iteration) / "TH_output.csv")

    @property
    def config_path(self) -> Path:
        return self.scenario_dir / CONFIG_FILENAME

    def main(self) -> None:
        readers = {
            "openmc": self._read_openfoam,
        }
        try:
            read = readers[self.thermo_code]
        except KeyError:
            raise ValueError(
                f"Code thermohydraulique non supporté : {self.thermo_code!r} "
                f"(supportés : {', '.join(readers)})"
            ) from None

        logger.info("Lecture des sorties %s (itération %d)",
                    self.thermo_code, self.iteration)
        read()

    def _read_openfoam(self) -> None:
            self.opemfoam_output.scenario = self.scenario
            self.opemfoam_output.casename = self.casename
            self.opemfoam_output.iteration = self.iteration
            self.opemfoam_output.main()