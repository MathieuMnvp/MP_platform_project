import logging
import sys

from Coupling.MainCoupling import MainCoupling
from Utils.JSON_server import JSON_server
from Utils.Tee import Tee

MCG = MainCoupling()
JS = JSON_server()

###########################

casename = "Kolmogorov-Smirnov"
scenario = "Statique"

###########################

JS.json_server("casename", casename)
JS.json_server("scenario", scenario)

MCG.casename = casename
MCG.scenario = scenario

with Tee("log.txt"):
    logging.basicConfig(
        level=logging.INFO,          # niveau par défaut : bibliothèques en INFO
        format="%(asctime)s [%(levelname)s] %(name)s : %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )

    for pkg in ("Coupling", "Utils", "__main__", "pandas"):
        logging.getLogger(pkg).setLevel(logging.DEBUG)

    MCG.main(restart=True)

#Pour repartir de la dernière itération de la simulation "casename", utiliser restart=True