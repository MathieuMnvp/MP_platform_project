import os
import sys
import shutil
import time
import subprocess
import re

__all__ = ["ThInputGenerator"]

class ThInputGenerator:

    def __init__(self):

        #Parameters
        #Variables
        self._iteration = 0
        self._casename = "default"

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
    def results_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration), "Thermohydraulics")


    def main(self):

        start = time.time()

        results_dir = self.results_dir
        iteration = self.iteration
        casename = self.casename

        print("TH iteration:", iteration)
        print("Copie des fichiers de référence en cours.")
        self.copy_reference(results_dir, iteration)
        #if iteration != 0 :
            #self.copy_last_timestep(results_dir, iteration, casename)
            #self.change_startfrom(results_dir)
        print("Calcul TH en cours...")
        self.run_simulation(results_dir)

        end = time.time()
        print(f"Calcul TH terminé en {round(end-start, 0)}s")

    def copy_reference(self, results_dir, iteration):

        if iteration == 0:
            src_dir = os.path.join(os.getcwd(), "Thermohydraulics", "buoyantSimple_PWR_1st_iteration")
        else:
            src_dir = os.path.join(os.getcwd(), "Thermohydraulics", "buoyantSimple_PWR_next_iteration")
        shutil.copytree(src_dir, results_dir)

    def copy_last_timestep(self, results_dir, iteration, casename):

        previous_timestep_dir = os.path.join(os.getcwd(), "Results", casename, str(iteration-1), "Thermohydraulics")
        
        time_dirs = [
        d for d in os.listdir(previous_timestep_dir)
        if os.path.isdir(os.path.join(previous_timestep_dir, d))
        and re.fullmatch(r"\d+(\.\d+)?", d)]

        time_dirs_sorted = sorted(time_dirs, key=lambda x: float(x))
        last_timestep_dir = time_dirs_sorted[-1]

        print("Le dernier fichier temporel est:", last_timestep_dir)

        previous_dir = os.path.join(previous_timestep_dir, last_timestep_dir)

        new_dir = os.path.join(results_dir, last_timestep_dir)

        shutil.copytree(previous_dir, new_dir, dirs_exist_ok=True)

    def change_startfrom(self, results_dir):

        controldict_path = os.path.join(results_dir, "system", "controlDict")

        with open(controldict_path, "r") as file:
            for num, line in enumerate(file, start=1):
                if "startFrom" in line:
                    target_line = num

        with open(controldict_path, "r") as file:
            to_modify = file.readlines()

        to_modify[target_line - 1] = "startFrom       latestTime;\n"

        with open(controldict_path, "w") as file:
            file.writelines(to_modify)
                           

    def run_simulation(self, results_dir):

        subprocess.run(["buoyantSimpleFoam"], cwd=results_dir)

if __name__ == "__main__":
    try:
        ThInputGenerator().main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
