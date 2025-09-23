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
        self.NN = 24 #Number of nodes
        self.P_target = 6.14035e6  

    def run(self):
        start=time.time()
        results_dir = self.results_dir
        os.makedirs(results_dir, exist_ok=True)
        self.output_read()
        self.output_plot()
        end=time.time()
        print(f"Output reading took {round(end-start, 0)}s")

    def output_read(self):

        NN = self.NN
        P_target = self.P_target
        results_dir = self.results_dir

        with openmc.StatePoint(os.path.join(results_dir, "statepoint.100.h5")) as sp:
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
        print(self.z_list)
         
        self.z_values = np.arange(1, NN+1)     

    def output_plot(self):

        plt.plot(self.z_values, self.z_list, marker="o", linestyle="-")

        plt.xlabel("Nodes")
        plt.ylabel("Power in Watts")
        plt.title("Power in a node")
        plt.grid(True)
        plt.savefig(os.path.join(self.results_dir, "mesh_power.png"), dpi=300, bbox_inches="tight")

        #P_tot = h.sum()
        #P_cells = P_target * tally_power / P_tot
