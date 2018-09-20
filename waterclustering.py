from PELEOutputParser.PELESimulation import Simulation
import numpy as np
from numpy import isnan


SIMULATION_DIR = "/home/municoy/LocalResults/CGL_4HIP_REF/"

METRIC_COL = 7

simulation = Simulation(SIMULATION_DIR, sim_type="Adaptive")

simulation.getOutputFiles()

waterBenergy = []
waterCenergy = []

for report in simulation.iterateOverReports:
    for value in report.getMetric(metric_name="waterB"):
        if value > 100 or isnan(value) or value < -100:
            continue
        waterBenergy.append(value)
    for value in report.getMetric(metric_name="waterC"):
        if value > 100 or isnan(value) or value < -100:
            continue
        waterCenergy.append(value)

print("Water B Binding Energy mean: " + str(np.mean(waterBenergy)))
print("Water C Binding Energy mean: " + str(np.mean(waterCenergy)))
