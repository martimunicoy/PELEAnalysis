# Repo Imports
from PELETools.TimeCalculator.TimeStructures import TimeStructure


class Step(TimeStructure):

    def __str__(self):
        return "PELE Step time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())


class Perturbation(TimeStructure):

    def __str__(self):
        return "Perturbation time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())


class ANM(TimeStructure):

    def __str__(self):
        return "ANM time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())


class SideChain(TimeStructure):

    def __str__(self):
        return "SideChain time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())


class Minimization(TimeStructure):

    def __str__(self):
        return "Minimization time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())
