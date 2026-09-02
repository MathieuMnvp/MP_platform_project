import os
import time
import shutil
import time
import subprocess

__all__ = ["OpenFOAMInputGenerator"]

class OpenFOAMInputGenerator:

    def __init__(self):
        self._iteration = 0
        self._casename = "default"
        self._scenario = "default"
        
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
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, value):
        self._scenario = value 

    @property
    def results_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration), "Thermohydraulics")

    @property
    def scenario_dir(self):
        return os.path.join(os.getcwd(), "Scenarios", self.scenario)   

    def main(self):
        start = time.time()

        results_dir = self.results_dir
        iteration = self.iteration

        print("Copie des fichiers de référence en cours.")
        self.copy_reference(results_dir, iteration)
        print("Calcul TH en cours...")
        self.run_simulation(results_dir)
        self.reconstruct_results(results_dir)

        end = time.time()
        print(f"Calcul TH terminé en {round(end-start, 0)}s")

    def copy_reference(self, results_dir, iteration):
        if iteration == 1:
            src_dir = os.path.join(os.getcwd(), "Scenarios", self.scenario, "openfoam", f"{self.scenario}_openfoam_1st_iteration")
        else:
            src_dir = os.path.join(os.getcwd(), "Scenarios", self.scenario, "openfoam", f"{self.scenario}_openfoam_next_iteration")
        shutil.copytree(src_dir, results_dir)        

    def run_simulation(self, results_dir):
        subprocess.run(["decomposePar", "-force"], cwd=results_dir, check=True)
        subprocess.run(["mpirun", "--use-hwthread-cpus", "-np", "16", "buoyantSimpleFoam", "-parallel"], cwd=results_dir, check=True)

    def reconstruct_results(self, results_dir):
        subprocess.run(["reconstructPar", "-latestTime"], cwd=results_dir, check=True)