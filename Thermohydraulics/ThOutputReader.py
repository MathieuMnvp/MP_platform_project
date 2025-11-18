import os
import sys
import subprocess
import numpy as np
import pandas as pd
import vtk
import time
import matplotlib.pyplot as plt
import re

__all__ = ["ThOutputReader"]

class ThOutputReader:

    def __init__(self):

        self.xmin = 0.0004035
        self.xmax = 0.2149095
        self.ymin = 0.0004035
        self.ymax = 0.2149095
        self.zmin = 0
        self.zmax = 2.005613
        self.nx = 34
        self.ny = 34
        self.nz = 24
        self.mc_samples_per_voxel = 5000
        self.seed = 42

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
    
    @property
    def output_dir(self):
        return os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration), "TH_output.csv")


    def main(self):

        start=time.time()

        print("Lecture des résultats TH en cours...")

        results_dir = self.results_dir
        output_dir = self.output_dir
        bounds = (self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax)

        self.export_openfoam_to_vtk(results_dir)
        vtu_path = self.find_latest_vtu(results_dir)
        ug = self.read_unstructured_grid(vtu_path)
        
        ix, iy, iz, Tavg, Ravg, extras = self.monte_carlo_voxel_average(
            ug, bounds, self.nx, self.ny, self.nz,
            self.mc_samples_per_voxel, self.seed) 
        
        data = {"ix": ix, "iy": iy, "iz": iz,   
                "T": Tavg, "rho" : Ravg,
                "valid": extras["valid"]}
        
        df = pd.DataFrame(data)
        df.to_csv(output_dir, index=False, float_format="%.8f")
        self.output_plot(self.nz, output_dir)
        print(f"Écriture de {output_dir} finie.")

        end=time.time()
        print(f"Lecture des résultats TH en {round(end-start, 0)}s")


    def export_openfoam_to_vtk(self, results_dir):
        
        subprocess.run(["postProcess", "-func", "writeCellCentres", "-latestTime"], cwd=results_dir)
        subprocess.run(["foamToVTK", "-latestTime"], cwd=results_dir)

    def find_latest_vtu(self, results_dir):

        time_dirs = [
        d for d in os.listdir(results_dir)
        if os.path.isdir(os.path.join(results_dir, d))
        and re.fullmatch(r"\d+(\.\d+)?", d)]

        time_dirs_sorted = sorted(time_dirs, key=lambda x: float(x))
        last_timestep_dir = time_dirs_sorted[-1]
        vtu_file = os.path.join(results_dir, "VTK", f'Thermohydraulics_{str(last_timestep_dir)}', "internal.vtu")
        return vtu_file

    def read_unstructured_grid(self, vtu_path: str):

        r = vtk.vtkXMLUnstructuredGridReader()
        r.SetFileName(vtu_path)
        r.Update()
        ug = r.GetOutput()
        return ug

    def output_plot(self, NN, output_dir):

        water_data = {}
        datas = pd.read_csv(output_dir, usecols=["ix", "iy", "iz", "T", "rho", "valid"])

        for _, row in datas.iterrows():
            x , y, z = row["ix"], row["iy"], row["iz"]
            water_data.setdefault(x, {}).setdefault(y, {})[z] = {col: row[col] for col in datas.columns if col not in ("x", "y", "z")}

        z_values = np.arange(1, NN+1)  
        z_list = []
        for z in range (1, NN+1):
            xy_list = []
            for y in range(1, 18):
                for x in range(1, 18):
                    xy_list.append(water_data[x][y][z]["T"])
            z_list.append(np.mean(xy_list))
            xy_list.clear()

        plt.plot(z_values, z_list, marker="o", linestyle="-")

        plt.xlabel("Nodes")
        plt.ylabel("Temperature in Kelvins")
        plt.title("Temperature for the node")
        plt.grid(True)
        plt.savefig(os.path.join(os.getcwd(), "Results", self.casename, str(self.iteration),"Z water temperature plot"), dpi=300, bbox_inches="tight")
        print("Water temperature plot created")
    
    # Méthode Monte-Carlo 

    def build_image_grid(self, bounds, nx, ny, nz):
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        sx = (xmax - xmin) / nx
        sy = (ymax - ymin) / ny
        sz = (zmax - zmin) / nz
        return (xmin, ymin, zmin), (sx, sy, sz)

    def voxel_bounds(self, origin, spacing, i, j, k): 
        ox, oy, oz = origin
        sx, sy, sz = spacing
        return (ox + (i-1)*sx, ox + i*sx,
                oy + (j-1)*sy, oy + j*sy,
                oz + (k-1)*sz, oz + k*sz)

    def random_points(self, x0, x1, y0, y1, z0, z1, n):
        r = np.random.rand(n, 3)
        r[:,0] = x0 + (x1 - x0)*r[:,0]
        r[:,1] = y0 + (y1 - y0)*r[:,1]
        r[:,2] = z0 + (z1 - z0)*r[:,2]
        return r

    def extract_cell_scalar_getter(self, ugrid, name):
        arr = ugrid.GetCellData().GetArray(name)
        if arr is None:
            raise RuntimeError(f"Champ CellData '{name}' introuvable dans le VTU.")
        def get_val(cid):
            return arr.GetTuple1(cid)
        return get_val

    def monte_carlo_voxel_average(self, ugrid, bounds, nx, ny, nz,
                                samples_per_voxel, seed): 
        
        np.random.seed(seed) 

        origin, spacing = self.build_image_grid(bounds, nx, ny, nz)

        ncell = nx * ny * nz
        IX = np.empty(ncell, dtype=np.int64)
        IY = np.empty(ncell, dtype=np.int64)
        IZ = np.empty(ncell, dtype=np.int64)
        Tm = np.full(ncell, np.nan)
        Rm = np.full(ncell, np.nan)
        valid = np.zeros(ncell, dtype=np.int32)

        get_T = self.extract_cell_scalar_getter(ugrid, "T")
        get_R = self.extract_cell_scalar_getter(ugrid, "rho_post")

        locator = vtk.vtkStaticCellLocator()
        locator.SetDataSet(ugrid)
        locator.BuildLocator()

        idx = 0
        for j in range(1, ny+1):          
            for i in range(1, nx+1):      
                for k in range(1, nz+1):  
                    ix = i
                    iy = j
                    iz = k
                    IX[idx], IY[idx], IZ[idx] = ix, iy, iz

                    x0,x1,y0,y1,z0,z1 = self.voxel_bounds(origin, spacing, i, j, k)
                    pts = self.random_points(x0, x1, y0, y1, z0, z1, samples_per_voxel)

                    rsum = 0.0
                    tsum = 0.0
                    cnt = 0
                    for p in pts:
                        cid = locator.FindCell(p.tolist())  # -1 si hors maillage
                        if cid >= 0:
                            tsum += get_T(cid)
                            rsum += get_R(cid)
                            cnt += 1

                    if cnt > 0:
                        Tm[idx] = tsum / cnt
                        Rm[idx] = rsum / cnt
                        valid[idx] = cnt

                    idx += 1

        extras = {"valid": valid}
        return IX, IY, IZ, Tm, Rm, extras


if __name__ == "__main__":
    try:
        ThOutputReader().main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

