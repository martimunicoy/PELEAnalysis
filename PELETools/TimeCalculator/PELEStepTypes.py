# Repo Imports
from PELETools.TimeCalculator.TimeStructures import TimeStructure


class Step(TimeStructure):

    name = "Step"

    def __str__(self):
        return "PELE " + self.name + " time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())


class Perturbation(TimeStructure):

    name = "Perturbation"

    def __str__(self):
        return self.name + " time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())


class ANM(TimeStructure):

    name = "ANM"

    def __str__(self):
        return self.name + " time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())


class SideChain(TimeStructure):

    name = "SideChain"

    def __str__(self):
        return self.name + " time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())


class Minimization(TimeStructure):

    name = "Minimization"

    def __str__(self):
        return self.name + " time: " + \
               "---Average time: " + str(self.calculate_average()) + \
               "---Variance time: " + str(self.calculate_variance()) + \
               "---Standard Deviation: " + str(self.calculate_standard_deviation())


PELE_STEP_TYPES = [Step, Perturbation, ANM, SideChain, Minimization]
