import openmc
import numpy as np
import os
import time
import sys
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Image

__all__ = ["NeOutputReader"]

class NeOutputReader:

    def __init__(self):
        
        #Geometry
        self.nx = 17
        self.ny = 17

        #Variables
        self._NN = 1 #Number of nodes
        self._P_target = 1 #Power of an assembly in W
        self._batches = 0
        self._iteration = 0
        self._casename = "default"

    @property
    def NN(self):
        return self._NN

    @NN.setter
    def NN(self, value):
        if value <= 0:
            raise ValueError("NN must be > 0")
        self._NN = value

    @property
    def P_target(self):
        return self._P_target
    
    @P_target.setter
    def P_target(self, value):
        if value <= 0:
            raise ValueError("P_target must be > 0")
        self._P_target = value        

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
    def output_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(int(self.iteration)+1), "NE_output.csv")
    
    @property
    def results_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration), "Neutronics")


    def main(self):
    
        start=time.time()

        print("Lecture des données NE en cours...")

        NN = int(self._NN)
        output_dir = self.output_dir
        results_dir = self.results_dir
        P_target = self.P_target
        os.makedirs(results_dir, exist_ok=True)

        tally_power, tally_id = self.output_read(results_dir)
        self.output_plot(tally_id, tally_power, P_target, NN)
        ix, iy, iz, Pw = self.output_file_creation(tally_id, tally_power, P_target, NN)

        data = {"ix": ix, "iy": iy, "iz": iz, "Power": Pw}
        
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        df.to_csv(output_dir, index=False, float_format="%.8f")
        print(f"Écriture de {output_dir} finie.")

        end=time.time()
        print(f"Lecture des résultats NE en {round(end-start, 0)}s")

    def output_read(self, results_dir):

        n = self.batches

        with openmc.StatePoint(os.path.join(results_dir, f"statepoint.{n}.h5")) as sp: 
            tally = sp.get_tally(name="heating_per_cell")
            tally_power = tally.mean.ravel()
            tally_id =  tally.filters[0].bins 

        return tally_power, tally_id
    
    def output_file_creation(self, tally_id, tally_power, P_target, NN):

        print("CSV output file writing...")
        nz = NN
        nx = self.nx
        ny = self.ny

        ncell = nx * ny * nz
        IX = np.empty(ncell, dtype=np.int64)
        IY = np.empty(ncell, dtype=np.int64)
        IZ = np.empty(ncell, dtype=np.int64)
        Pw = np.full(ncell, np.nan)

        ix = str(tally_id)[5:7]
        iy = str(tally_id)[3:5]
        iz = str(tally_id)[1:3]

        P_tot = tally_power.sum()
        P_cells = np.round(P_target * tally_power / P_tot, 5)

        idx = 0
        for j in range(1, ny+1):          
            for i in range(1, nx+1):      
                for k in range(1, nz+1):  
                    ix = str(tally_id[idx])[5:7]
                    iy = str(tally_id[idx])[3:5]
                    iz = str(tally_id[idx])[1:3]
                    IX[idx], IY[idx], IZ[idx] = ix, iy, iz
                    Pw[idx] = P_cells[idx]
                    idx += 1

        print("CSV output file writed")
        return IX, IY, IZ, Pw


    def output_plot(self, tally_id, tally_power, P_target, NN):

        print("Mesh power plot creation...")
        P_tot = tally_power.sum()
        P_cells = np.round(P_target * tally_power / P_tot, 5)

        heat_power = {cid: val for cid, val in zip(tally_id, P_cells)}

        self.z_list = []
        for z in range (1, NN+1):
            if z < 10:
                z_value = str(z).zfill(2)
            else:
                z_value = z
            xy_list = []
            for key in heat_power.keys():
                if str(key)[1:3] == str(z_value):
                    xy_list.append(heat_power[key])
            self.z_list.append(np.mean(xy_list))
        self.z_values = np.arange(1, NN+1)  

        plt.plot(self.z_values, self.z_list, marker="o", linestyle="-")

        plt.xlabel("Nodes")
        plt.ylabel("Power in Watts")
        plt.title("Power in a node")
        plt.grid(True)
        plt.savefig(os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration),"Z mesh power plot"), dpi=300, bbox_inches="tight")
        print("Mesh power plot created")

if __name__ == "__main__":
    try:
        NeOutputReader().main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)