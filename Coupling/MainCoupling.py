from Neutronics.NeInputGenerator import NeInputGenerator
from Neutronics.NeOutputReader import NeOutputReader
from Thermohydraulics.ThInputGenerator import ThInputGenerator
from Thermohydraulics.ThOutputReader import ThOutputReader

NIG = NeInputGenerator()
NOR = NeOutputReader()
TIG = ThInputGenerator()
TOR = ThOutputReader()


__all__ = ["MainCoupling"]

class MainCoupling:

    def __init__(self):
        #Variables
        self._NN = 1 #Number of nodes
        self._batches = 0
        self._inactive = 0
        self._particles = 0
        self._iteration = 0
        self._casename = "default"
        self._P_target = 1 #Power of an assembly in W
        self._start_iteration = 1
        self._last_iteration = 1
        self._restart_from_NE = False
    
    @property
    def NN(self):
        return self._NN

    @NN.setter
    def NN(self, value):
        if value <= 0:
            raise ValueError("NN must be > 0")
        self._NN = value

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
    def particles(self):
        return self._particles

    @particles.setter
    def particles(self, value):
        if value <= 0:
            raise ValueError("particles must be >0")
        self._particles = value

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
    def P_target(self):
        return self._P_target
    
    @P_target.setter
    def P_target(self, value):
        if value <= 0:
            raise ValueError("P_target must be > 0")
        self._P_target = value    

    @property
    def start_iteration(self):
        return self._start_iteration
    
    @start_iteration.setter
    def start_iteration(self, value):
        if value <= 0:
            raise ValueError("start_iteration must be > 0")
        if value > self.last_iteration:
            raise ValueError("start_iteration must be <= than last_iteration")
        self._start_iteration = value   

    @property
    def last_iteration(self):
        return self._last_iteration
    
    @last_iteration.setter
    def last_iteration(self, value):
        if value <= 0:
            raise ValueError("last_iteration must be > 0")
        self._last_iteration = value

    @property
    def restart_from_NE(self):
        return self._restart_from_NE
    
    @restart_from_NE.setter
    def restart_from_NE(self, value):
        if value != False and value !=True:
            raise ValueError("restart_from_NE must True or False")
        self._restart_from_NE = value     


    def main(self):
        if self.restart_from_NE:
            iteration = int(self.start_iteration-1)
            NIG.NN = self.NN
            NIG.batches = self.batches
            NIG.inactive = self.inactive
            NIG.particles = self.particles
            NIG.casename = self.casename
            NIG.iteration = iteration
            NIG.main()

            NOR.NN = self.NN
            NOR.P_target = self.P_target
            NOR.batches = self.batches
            NOR.casename = self.casename
            NOR.iteration = iteration
            NOR.main()


        for iteration in range(self.start_iteration, self.last_iteration):
            print(iteration)
            
            TIG.casename = self.casename
            TOR.casename = self.casename
            TIG.iteration = iteration
            TOR.iteration = iteration
            TIG.main()
            TOR.main()

            NIG.NN = self.NN
            NIG.batches = self.batches
            NIG.inactive = self.inactive
            NIG.particles = self.particles
            NIG.casename = self.casename
            NIG.iteration = iteration
            NIG.main()

            NOR.NN = self.NN
            NOR.P_target = self.P_target
            NOR.batches = self.batches
            NOR.casename = self.casename
            NOR.iteration = iteration
            NOR.main()