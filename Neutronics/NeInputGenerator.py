import os
import sys
from Neutronics.openmc.OpenMcInputGenerator import OpenMcInputGenerator
from Utils.json_utils import json_reader

OMI = OpenMcInputGenerator()

__all__ = ["NeInputGenerator"]

class NeInputGenerator:

    def __init__(self):
        #Variables
        self._iteration = 0
        self._casename = "default"
        self._scenario ="default"
        self._neutro_code = "default"

    @property
    def iteration(self):
        return self._iteration

    @iteration.setter
    def iteration(self, value):
        self._iteration = value

    @property
    def casename(self):
        return self._casename

    @casename.setter
    def casename(self, value):
        self._casename = value 

    @property
    def neutro_code(self):
        return self._neutro_code

    @neutro_code.setter
    def neutro_code(self, value):
        self._neutro_code = value 

    @property
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, value):
        self._scenario = value 

    @property
    def scenario_dir(self):
        return os.path.join(os.getcwd(), "Scenarios", self.scenario)    

    def main(self):
        self.input_generator()
    
    def input_generator(self):
        if self.neutro_code == "openmc":
            config_file = os.path.join(self.scenario_dir, "config.json")
            data = json_reader(config_file)
            OMI.batches = data["openmc"]["batches"]
            OMI.inactive = data["openmc"]["inactive"]
            OMI.scenario = self.scenario
            OMI.casename = self.casename
            OMI.iteration = self.iteration
            OMI.main()

if __name__ == "__main__":
    try:
        NeInputGenerator().main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)