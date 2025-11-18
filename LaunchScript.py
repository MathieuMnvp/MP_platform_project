from Coupling.MainCoupling import MainCoupling

MCG = MainCoupling()

NN = 24
batches = 200
inactive = 20
particles = 10000
P_target = 6.14035e6
casename = "Test1"
start_iteration = 1
last_iteration = 20
restart_from_NE = False

MCG.NN = NN
MCG.batches = batches
MCG.inactive = inactive
MCG.particles = particles
MCG.P_target = P_target
MCG.casename = casename
MCG.last_iteration = last_iteration
MCG.start_iteration = start_iteration
MCG.restart_from_NE = restart_from_NE

MCG.main()



