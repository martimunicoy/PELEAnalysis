# Repo Imports
from PELETools.TimeCalculator.TimeStructures import TimeStructure


class Step(TimeStructure):

    name = "Step"
    name_to_search_in_log_file = "step time"
    time_position_in_log_file = 0

    def __str__(self):
        return "PELE " + self.name + " time: \n" + \
               "---Average time: " + str(self.calculate_average()) + "\n" \
               "---Variance time: " + str(self.calculate_variance()) + "\n" \
               "---Standard Deviation: " + str(self.calculate_standard_deviation()) + "\n"


class Perturbation(TimeStructure):

    name = "Perturbation"
    name_to_search_in_log_file = "Perturbation Ef:"
    time_position_in_log_file = -1  # Last position

    def __str__(self):
        return self.name + " time: \n" + \
               "---Average time: " + str(self.calculate_average()) + "\n"\
               "---Variance time: " + str(self.calculate_variance()) + "\n"\
               "---Standard Deviation: " + str(self.calculate_standard_deviation()) + "\n"


class ANM(TimeStructure):

    name = "ANM"
    name_to_search_in_log_file = "ANM Ef:"
    time_position_in_log_file = -1  # Last position

    def __str__(self):
        return self.name + " time: \n" + \
               "---Average time: " + str(self.calculate_average()) + "\n"\
               "---Variance time: " + str(self.calculate_variance()) + "\n"\
               "---Standard Deviation: " + str(self.calculate_standard_deviation()) + "\n"


class SideChain(TimeStructure):

    name = "SideChain"
    name_to_search_in_log_file = "Side Chain Prediction Ef"
    time_position_in_log_file = -1  # Last position

    def __str__(self):
        return self.name + " time: \n" + \
               "---Average time: " + str(self.calculate_average()) + "\n"\
               "---Variance time: " + str(self.calculate_variance()) + "\n"\
               "---Standard Deviation: " + str(self.calculate_standard_deviation()) + "\n"


class Minimization(TimeStructure):

    name = "Minimization"
    name_to_search_in_log_file = "Minimization Ef:"
    time_position_in_log_file = -1  # Last position

    def __str__(self):
        return self.name + " time: \n" + \
               "---Average time: " + str(self.calculate_average()) + "\n"\
               "---Variance time: " + str(self.calculate_variance()) + "\n"\
               "---Standard Deviation: " + str(self.calculate_standard_deviation()) + "\n"


PELE_STEP_TYPES = [Step, Perturbation, ANM, SideChain, Minimization]
