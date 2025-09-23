import openmc
import os
import time
from PIL import Image

__all__ = ["NeInputGenerator"]

class NeInputGenerator:

    def __init__(self):

        self.results_dir = os.path.join(os.getcwd(), "results")

        #ID
        self.fuel_material_id=1
        self.helium_material_id=2
        self.zircaloy_material_id=3
        self.AIC_material_id=4
        self.SS304_material_id=5
        self.water_material_id=6

        #Parameters
        #General
        self.AH = 200.5613 #Active height
        self.CP = 1.2618 #Cell pitch
        self.HCP = self.CP/2 #Half of a cell pitch
        self.AP = 21.5313 #Assembly pitch
        self.AG = 0.04035 #Inter-assembly half gap

        #Fuel
        self.FP = 0.4107 #Fuel pellet radius
        self.ICF = 0.4186 #Inner clad radius
        self.OCF = 0.4757 #Outer clad radius

        #Control rod
        self.AR = 0.3844 #Absorber rod radius
        self.ICC = 0.3879 #Inner cladding radius
        self.OCC = 0.4863 #Outer cladding radius
        self.IGT = 0.5618 #Inner guide tube radius
        self.OGT = 0.6029 #Outer guide tube radius

        #Instrument tube
        self.IIT = 0.5598 #Inner instrument tube radius
        self.OIT = 0.6059 #Outer instrument tube radius

        #Variables
        self.NN = 24 #Number of nodes
        self.NH = self.AH/self.NN #Height of a node

        #Materials and Geometry
        self.cells = []
        self.tally_cells = []
        self.control_rod_list = [40, 43, 46, 55, 65, 88, 91, 94, 97, 100, 139, 142, 148, 151, 190, 193, 196, 199, 202, 225, 235, 244, 247, 250]
        self.instrument_tube_list = [145]

    def run(self):
        start=time.time()
        results_dir = self.results_dir
        os.makedirs(results_dir, exist_ok=True)
        self.geometry_creation()
        self.tallies_creation()
        self.settings_creation()
        self.geometry_plot()
        self.simulation_runner()
        end=time.time()
        print(f"Simulation took {round(end-start, 0)}s")

    def geometry_creation(self):

        results_dir = self.results_dir

        fuel_material_id = self.fuel_material_id
        helium_material_id = self.helium_material_id
        zircaloy_material_id = self.zircaloy_material_id
        AIC_material_id = self.AIC_material_id
        SS304_material_id = self.SS304_material_id
        water_material_id = self.water_material_id

        AH = self.AH 
        CP = self.CP 
        HCP = self.HCP 
        AP = self.AP 
        AG = self.AG 
        FP = self.FP
        ICF = self.ICF 
        OCF = self.OCF 
        AR = self.AR 
        ICC = self.ICC
        OCC = self.OCC 
        IGT = self.IGT 
        OGT = self.OGT
        IIT = self.IIT
        IOT = self.OIT
        NN = self.NN 
        NH = self.NH 

        cells = self.cells
        tally_cells = self.tally_cells
        control_rod_list = self.control_rod_list
        instrument_tube_list = self.instrument_tube_list

        mats = openmc.Materials()

        for z in range(1, NN+1):
            for y in range(1, 35):
                for x in range(1, 35):
                    ID = water_material_id * 1000000 + z*10000 + y*100 + x
                    water = openmc.Material(material_id=ID, name="water")
                    water.set_density('sum')
                    water.add_nuclide('H1', 4.6360E-02)
                    water.add_nuclide('O16', 2.3180E-02)
                    mats.append(water)
                    water_surface = openmc.model.RectangularParallelepiped(HCP*(x-1)+AG, HCP*(x)+AG, HCP*(y-1)+AG, HCP*(y)+AG, NH*(z-1), NH*(z))
                    water_cell = openmc.Cell(cell_id=ID, fill=water, region=-water_surface)
                    cells.append(water_cell)

        fuel = openmc.Material(material_id=fuel_material_id, name="fuel")
        fuel.set_density('sum')
        fuel.add_nuclide('O16', 4.5379E-02)
        fuel.add_nuclide('U234', 5.4434E-06)
        fuel.add_nuclide('U235', 6.4320E-04)
        fuel.add_nuclide('U236', 2.9462E-06)
        fuel.add_nuclide('U238', 2.2038E-02)
        mats.append(fuel)

        helium = openmc.Material(material_id=helium_material_id, name="helium")
        helium.add_nuclide('He3', 4.8089E-10)
        helium.add_nuclide('He4', 2.4044E-04)
        mats.append(helium)

        zircaloy = openmc.Material(material_id=zircaloy_material_id, name="zircaloy")
        zircaloy.set_density('sum')
        zircaloy.add_nuclide('Cr50', 3.2818E-06)
        zircaloy.add_nuclide('Cr52', 6.3287E-05)
        zircaloy.add_nuclide('Cr53', 7.1762E-06)
        zircaloy.add_nuclide('Cr54', 1.7863E-06)
        zircaloy.add_nuclide('Fe54', 8.6321E-06)
        zircaloy.add_nuclide('Fe56', 1.3551E-04)
        zircaloy.add_nuclide('Fe57', 3.1294E-06)
        zircaloy.add_nuclide('Fe58', 4.1647E-07)
        zircaloy.add_nuclide('O16', 3.0692E-04)
        zircaloy.add_nuclide('Sn112', 4.6532E-06)
        zircaloy.add_nuclide('Sn114', 3.1661E-06)
        zircaloy.add_nuclide('Sn115', 1.6310E-06)
        zircaloy.add_nuclide('Sn116', 6.9750E-05)
        zircaloy.add_nuclide('Sn117', 3.6842E-05)
        zircaloy.add_nuclide('Sn118', 1.1619E-04)
        zircaloy.add_nuclide('Sn119', 4.1207E-05)
        zircaloy.add_nuclide('Sn120', 1.5629E-04)
        zircaloy.add_nuclide('Sn122', 2.2210E-05)
        zircaloy.add_nuclide('Sn124', 2.7775E-05)
        zircaloy.add_nuclide('Zr90', 2.1733E-02)
        zircaloy.add_nuclide('Zr91', 4.7393E-03)
        zircaloy.add_nuclide('Zr92', 7.2442E-03)
        zircaloy.add_nuclide('Zr94', 7.3413E-03)
        zircaloy.add_nuclide('Zr96', 1.1827E-03)
        mats.append(zircaloy)

        zmin = openmc.ZPlane(z0=0)
        zmax = openmc.ZPlane(z0=AH)

        for y in range(1, 18):
                for x in range(1, 18):
                        helium_id = helium_material_id * 1000000 + y*100 + x
                        zircaloy_id = zircaloy_material_id * 1000000 + y*100 + x
                        fuel_help_surface = openmc.ZCylinder(x0=AG+(CP/2)+CP*(x-1), y0=AG+(CP/2)+CP*(y-1), r=0.4107)
                        helium_surface = openmc.ZCylinder(x0=AG+(CP/2)+CP*(x-1), y0=AG+(CP/2)+CP*(y-1), r=0.4186)
                        zircaloy_surface = openmc.ZCylinder(x0=AG+(CP/2)+CP*(x-1), y0=AG+(CP/2)+CP*(y-1), r=0.4757)
                        helium_cell = openmc.Cell(cell_id=helium_id, fill=helium, region= +zmin & -zmax & +fuel_help_surface & -helium_surface)
                        zircaloy_cell = openmc.Cell(cell_id=zircaloy_id, fill=zircaloy, region= +zmin & -zmax & +helium_surface & -zircaloy_surface)
                        cells.append(helium_cell)
                        cells.append(zircaloy_cell)
                        for z in range(1, NN+1):
                            fuel_id = fuel_material_id * 1000000 + z * 10000 + y * 100 + x
                            fuel_surface = openmc.ZCylinder(x0=AG+(CP/2)+CP*(x-1), y0=AG+(CP/2)+CP*(y-1), r=0.4107)
                            zlow = openmc.ZPlane(z0 = NH*(z-1))
                            zhigh = openmc.ZPlane(z0 = NH*(z))
                            fuel_cell = openmc.Cell(cell_id=fuel_id, fill=fuel, region= +zlow & -zhigh & -fuel_surface)
                            cells.append(fuel_cell)
                            tally_cells.append(fuel_cell)

        assembly_univ = openmc.Universe(name="assembly", cells=cells)

        world = openmc.model.RectangularParallelepiped(
            AG, CP*17+AG,   # x min/max
            AG, CP*17+AG,   # y min/max
            0, AH,   # z min/max
            boundary_type="reflective")

        root_cell = openmc.Cell(name="root", region=-world, fill=assembly_univ)

        geom = openmc.Geometry([root_cell])
        mats.export_to_xml(results_dir)
        geom.export_to_xml(results_dir)

    def tallies_creation(self):

        results_dir = self.results_dir
        tally_cells = self.tally_cells

        tally = openmc.Tally(name="heating_per_cell")
        tally.filters = [openmc.CellFilter(tally_cells)]
        tally.scores = ["heating"]
        openmc.Tallies([tally]).export_to_xml(results_dir)

    def settings_creation(self):

        AH = self.AH 
        CP = self.CP 
        AG = self.AG
        results_dir = self.results_dir

        settings = openmc.Settings()

        src = openmc.IndependentSource()
        src.space  = openmc.stats.Box((AG, AG, 0.0), (CP*17+AG, CP*17+AG, AH), only_fissionable=True)
        src.angle  = openmc.stats.Isotropic()
        src.energy = openmc.stats.Watt(2.0, 0.988)
        settings.source = src

        self.settings = settings
        settings.batches = 100
        settings.inactive = 10
        settings.particles = 1000
        settings.summary = False
        settings.export_to_xml(results_dir)

    def geometry_plot(self):

        AP = self.AP
        results_dir = self.results_dir

        plot = openmc.Plot()
        plot.basis = 'xy'                 
        plot.origin = (AP/2, AP/2, 200.0)    
        plot.width  = (AP, AP)      
        plot.pixels = (400, 400)         
        plot.color_by = 'material'  

        plots = openmc.Plots([plot])
        plots.export_to_xml(path=os.path.join(results_dir, "plots.xml"))

        openmc.plot_geometry(cwd=results_dir)

        ppm_file = os.path.join(results_dir, "plot_1.ppm")
        png_file = os.path.join(results_dir, "plot_1.png")

        if os.path.exists(ppm_file):
            img = Image.open(ppm_file)
            img.save(png_file)
            print(f"Image convertie : {png_file}")
        else:
            print("⚠️ Aucun fichier PPM trouvé")

    def simulation_runner(self):

        results_dir = self.results_dir
        openmc.run(cwd=results_dir, threads=12)

        n = self.settings.batches
        with openmc.StatePoint(f'./results/statepoint.{n}.h5') as sp:
            keff = sp.keff
            print(f'Final k-effective = {keff}')
