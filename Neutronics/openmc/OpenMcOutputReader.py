import openmc
import numpy as np
import os
import time
import sys
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Image
from Utils.json_utils import json_reader
import xml.etree.ElementTree as ET

__all__ = ["OpenMcOutputReader"]

class OpenMcOutputReader:

    def __init__(self):

        #Variables
        self._batches = 300
        self._iteration = 0
        self._scenario = "default"
        self._casename = "default"

    @property
    def batches(self):
        return self._batches

    @batches.setter
    def batches(self, value):
        if value <= 0:
            raise ValueError("batches must be > 0")
        self._batches = value

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
    def output_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration), "NE_output.csv")
    
    @property
    def results_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration), "Neutronics")
    
    @property
    def scenario_dir(self):
        return os.path.join(os.getcwd(), "Scenarios", self.scenario) 

    def main(self):
    
        start=time.time()

        print("Lecture des données NE en cours...")

        output_dir = self.output_dir
        results_dir = self.results_dir
        iteration = self.iteration

        self.extract_keff(results_dir, iteration)

        nx, ny, nz = self.extract_dim(results_dir)
        P_target = self.extract_power(self.scenario_dir)

        os.makedirs(results_dir, exist_ok=True)

        tally_power, tally_id, tally_stv_dev = self.output_read(results_dir, iteration)
        self.output_plot(tally_id, tally_power, P_target, nz)
        ix, iy, iz, Pw, Pw_std_dev = self.output_file_creation(tally_id, tally_power, tally_stv_dev, P_target)

        data = {"ix": ix, "iy": iy, "iz": iz, "Power": Pw, "Power_Std_Dev": Pw_std_dev}
        
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        df.to_csv(output_dir, index=False, float_format="%.8f")
        print(f"Écriture de {output_dir} finie.")

        end=time.time()
        print(f"Lecture des résultats NE en {round(end-start, 0)}s")

    def extract_keff(self, results_dir, iteration):

        n = self.batches

        with openmc.StatePoint(os.path.join(results_dir, f"statepoint.{n}.h5"), autolink=False) as sp: 
            keff = sp.keff           
            valeur = keff.nominal_value   
            sigma  = keff.std_dev

        keff_path = os.path.join(os.getcwd(), "Results", self.casename, "convergence.csv")
        os.makedirs(os.path.dirname(keff_path), exist_ok=True)
        
        nouvelle_ligne = pd.DataFrame({
            "iteration": [iteration],
            "keff": [valeur],
            "sigma_keff": [sigma]
        })

        if os.path.isfile(keff_path):
            df_existant = pd.read_csv(keff_path)
            df_final = pd.concat([df_existant, nouvelle_ligne], ignore_index=True)
        else:
            df_final = nouvelle_ligne

        df_final.to_csv(keff_path, index=False, float_format="%.6f")

    def extract_dim(self, results_dir):
        
        tree = ET.parse(os.path.join(results_dir, 'settings.xml'))
        root = tree.getroot()

        mesh = root.find("mesh[@id='1']")
        dimension = mesh.find('dimension').text
        dim = list(map(int, dimension.split()))  

        nx = dim[0]
        ny = dim[1]
        nz = dim[2]

        return nx, ny, nz
    
    def extract_power(self, scenario_dir):
        
        config_file = os.path.join(scenario_dir, "config.json")
        data = json_reader(config_file)
        P_target = data["power"]

        return P_target

    def output_read(self, results_dir, iteration):

        n = self.batches

        with openmc.StatePoint(os.path.join(results_dir, f"statepoint.{n}.h5"), autolink=False) as sp: 
            tally = sp.get_tally(name=f'heating_per_cell{iteration}')
            tally_power = tally.mean.ravel()
            tally_std_dev = tally.std_dev.ravel()
            tally_id =  tally.filters[0].bins

        return tally_power, tally_id, tally_std_dev
    
    def output_file_creation(self, tally_id, tally_power, tally_std_dev, P_target):
        print("Fichier de sortie CSV en écriture...")

        P_tot = tally_power.sum()
        scaling_factor = P_target / P_tot
        Pw = np.round(tally_power * scaling_factor, 5)
        Pw_std_dev = np.round(tally_std_dev * scaling_factor, 5)

        tally_id_array = np.array(tally_id)

        IX = tally_id_array[:, 0]
        IY = tally_id_array[:, 1]
        IZ = tally_id_array[:, 2]

        return IX, IY, IZ, Pw, Pw_std_dev


    def output_plot(self, tally_id, tally_power, P_target, nz):

        print("Mesh power plot creation...")
        P_tot = tally_power.sum()
        P_cells = np.round(P_target * tally_power / P_tot, 5)

        heat_power = {cid: val for cid, val in zip(tally_id, P_cells)}

        self.z_list = []
        for z in range (1, nz+1):
            xy_list = []
            for key in heat_power.keys():
                if str(key[-1]) == str(z):
                    xy_list.append(heat_power[key])
            self.z_list.append(np.mean(xy_list))
        self.z_values = np.arange(1, nz+1) 

        plt.clf()
        plt.plot(self.z_values, self.z_list, marker="o", linestyle="-")

        plt.xlabel("Nodes")
        plt.ylabel("Power in Watts")
        plt.title("Power in a node")
        plt.grid(True)
        plt.savefig(os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration),"Z mesh power plot"), dpi=300, bbox_inches="tight")
        print("Mesh power plot created")

if __name__ == "__main__":
    try:
        OpenMcOutputReader().main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)