# Repo Imports
from PELETools.TimeCalculator.TimeStructures import TimeStructure


class Step(TimeStructure):

    name = "Step"
    name_to_search_in_log_file = "step time"
    time_position_in_log_file = 0


class Perturbation(TimeStructure):

    name = "Perturbation"
    name_to_search_in_log_file = "Perturbation Ef:"
    time_position_in_log_file = -1  # Last position


class ANM(TimeStructure):

    name = "ANM"
    name_to_search_in_log_file = "ANM Ef:"
    time_position_in_log_file = -1  # Last position


class SideChain(TimeStructure):

    name = "SideChain"
    name_to_search_in_log_file = "Side Chain Prediction Ef"
    time_position_in_log_file = -1  # Last position


class Minimization(TimeStructure):

    name = "Minimization"
    name_to_search_in_log_file = "Minimization Ef:"
    time_position_in_log_file = -1  # Last position


PELE_STEP_TYPES = [Step, Perturbation, ANM, SideChain, Minimization]
