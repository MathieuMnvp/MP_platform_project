import os
import sys
from Thermohydraulics.openfoam.OpenFOAMOutputReader import OpenFOAMOutputReader

openfoam = OpenFOAMOutputReader()

__all__ = ["ThOutputReader"]

class ThOutputReader:

    def __init__(self):
        #Variables
        self._scenario = "default"
        self._iteration = 0
        self._thermo_code = "default"
        self._casename = "default"

    @property
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, value):
        self._scenario = value 

    @property
    def iteration(self):
        return self._iteration

    @iteration.setter
    def iteration(self, value):
        self._iteration = value

    @property
    def thermo_code(self):
        return self._thermo_code

    @thermo_code.setter
    def thermo_code(self, value):
        self._thermo_code = value

    @property
    def casename(self):
        return self._casename

    @casename.setter
    def casename(self, value):
        self._casename = value

    @property
    def results_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration), "Thermohydraulics")
    
    @property
    def output_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration), "TH_output.csv")

    def main(self):
        if self.thermo_code == "openfoam":
            openfoam.scenario = self.scenario
            openfoam.casename = self.casename
            openfoam.iteration = self.iteration
            openfoam.main()

if __name__ == "__main__":
    try:
        ThOutputReader().main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

