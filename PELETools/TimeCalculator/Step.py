# Repo Imports
from PELETools.TimeCalculator.TimeStructures import TimeStructure

class Step(TimeStructure):

    def __str__(self):
        return "PELE Step time: " + \
               "---Average time: " +