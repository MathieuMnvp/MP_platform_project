import openmc
import numpy as np
import os
import time
import matplotlib.pyplot as plt
from IPython.display import Image

__all__ = ["NeOutputReader"]

class NeOutputReader:

    def __init__(self):

        self.results_dir = os.path.join(os.getcwd(), "results")

        #Variables
        self._NN = 1 #Number of nodes
        self._P_target = 1 #Power of an assembly in W

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

    def run(self):
        start=time.time()
        results_dir = self.results_dir
        os.makedirs(results_dir, exist_ok=True)
        self.output_read()
        self.output_plot()
        end=time.time()
        print(f"Output reading took {round(end-start, 0)}s")

    def output_read(self):

        NN = int(self._NN)
        P_target = self._P_target
        results_dir = self.results_dir

        with openmc.StatePoint(os.path.join(results_dir, "statepoint.120.h5")) as sp: #corriger cela
            tally = sp.get_tally(name="heating_per_cell")
            tally_power = tally.mean.ravel()
            tally_id =  tally.filters[0].bins 

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

    def output_plot(self):

        plt.plot(self.z_values, self.z_list, marker="o", linestyle="-")

        plt.xlabel("Nodes")
        plt.ylabel("Power in Watts")
        plt.title("Power in a node")
        plt.grid(True)
        plt.savefig(os.path.join(self.results_dir, "mesh_power.png"), dpi=300, bbox_inches="tight")
