from NeInputGenerator import NeInputGenerator
from NeOutputReader import NeOutputReader

NIG = NeInputGenerator()
NOR = NeOutputReader()

NN = 24
batches = 220
inactive = 20
particles = 200000
P_target = 6.14035e6

NIG.NN = NN
NIG.batches = batches
NIG.inactive = inactive
NIG.particles = particles
NIG.run()

NOR.NN = NN
NOR.P_target = P_target
NOR.run()
