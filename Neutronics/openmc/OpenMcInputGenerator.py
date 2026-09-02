import os
import subprocess
import time
import importlib.util
import openmc

__all__ = ["OpenMcInputGenerator"]

class OpenMcInputGenerator:

    def __init__(self):
        self._processors = 0
        self._iteration = 0
        self._batches = 0
        self._inactive = 0
        self._casename = "default"
        self._scenario = "default"

    @property
    def processors(self):
        return self._processors

    @processors.setter
    def processors(self, value):
        if value <= 0:
            raise ValueError("start_iteration must be > 0")
        self._processors = value 

    @property
    def iteration(self):
        return self._iteration

    @iteration.setter
    def iteration(self, value):
        self._iteration = value

    @property
    def batches(self):
        return self._batches

    @batches.setter
    def batches(self, value):
        if value <= 0:
            raise ValueError("batches must be > 0")
        self._batches = value

    @property
    def inactive(self):
        return self._inactive

    @inactive.setter
    def inactive(self, value):
        if value < 0:
            raise ValueError("inactive must be >= 0")
        self._inactive = value

    @property
    def casename(self):
        return self._casename

    @casename.setter
    def casename(self, value):
        self._casename = value

    @property
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, value):
        self._scenario = value 

    @property
    def scenario_dir(self):
        return os.path.join(os.getcwd(), "Scenarios", self.scenario) 

    @property
    def results_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration), "Neutronics")

    def main(self):
        self.ID_reset()
        self.input_generator()
        self.simulation_runner()

    def ID_reset(self):
        openmc.Cell.used_ids.clear()
        openmc.Material.used_ids.clear()
        openmc.Surface.used_ids.clear()
        openmc.Universe.used_ids.clear()
        openmc.Tally.used_ids.clear()
        openmc.Filter.used_ids.clear()
        openmc.reset_auto_ids()

    def load_class_from_file(self, filepath, class_name):
        spec = importlib.util.spec_from_file_location("dynamic_module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return getattr(module, class_name)

    def input_generator(self):
        open_mc_input = self.scenario + "_" + "openmc" + ".py"
        openmc_file_path = os.path.join(self.scenario_dir, "openmc", open_mc_input)
        OpenMc = self.load_class_from_file(openmc_file_path, "OpenMCInput")
        OpenMc = OpenMc()
        OpenMc.batches = self._batches
        OpenMc.inactive = self._inactive
        OpenMc.iteration = self._iteration
        OpenMc.casename = self._casename
        OpenMc.main()

    def simulation_runner(self):
        start = time.time()
        results_dir = self.results_dir
        subprocess.run(["openmc", "--threads", "16"], cwd=results_dir, check=True)
        end = time.time()
        print(f"Simulation NE terminée en {round(end-start, 0)}s")

