import os
import sys
from Utils.json_utils import json_reader
from Neutronics.openmc.OpenMcOutputReader import OpenMcOutputReader

OOR = OpenMcOutputReader()

__all__ = ["NeOutputReader"]

class NeOutputReader:

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
        self.output_reader()

    def get_config_data(self):
        config_file = os.path.join(self.scenario_dir, "config.json")
        data = json_reader(config_file)
        return data
    
    def output_reader(self):
        data = self.get_config_data()
        if self.neutro_code == "openmc":
            OOR.batches = data["openmc"]["batches"]
            OOR.scenario = self.scenario
            OOR.casename = self.casename
            OOR.iteration = self.iteration
            OOR.main()

if __name__ == "__main__":
    try:
        NeOutputReader().main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)