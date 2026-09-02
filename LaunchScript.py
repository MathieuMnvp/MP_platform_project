from Coupling.MainCoupling import MainCoupling
from Utils.JSON_server import JSON_server
from Utils.Tee import Tee

MCG = MainCoupling()
JS = JSON_server()

###########################

casename = "Asmb_REP_test_validation"
scenario = "Statique"

###########################

JS.json_server("casename", casename)
JS.json_server("scenario", scenario)

MCG.casename = casename
MCG.scenario = scenario

with Tee("log.txt"):
    print("Simulation start")
    MCG.main(restart=False)

#Pour repartir de la dernière itération de la simulation "casename", utiliser restart=True