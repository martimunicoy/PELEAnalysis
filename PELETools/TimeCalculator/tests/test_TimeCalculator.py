# Project imports
from PELETools.TimeCalculator.TimeCalculator import *

# Libraries imports
from nose.tools import assert_equal, assert_true, assert_in, assert_almost_equal

FILES = ["PELETools/TimeCalculator/tests/data/logFile_1.txt",
         "PELETools/TimeCalculator/tests/data/logFile_2.txt",
         "PELETools/TimeCalculator/tests/data/logFile_3.txt"]


class TestTimeCalculator:

    def test_init_parameters(self):
        self.test_time_calculator = TimeCalculator(FILES, all_types=False)

        assert_equal(self.test_time_calculator.simulation_path, FILES)
        assert_true(hasattr(self.test_time_calculator, "_PELE_TimeStructures_dict"))

    def test_init_instantiate_only_step(self):
        self.test_time_calculator = TimeCalculator(FILES, all_types=False)
        step_dict = self.test_time_calculator.PELE_TimeStructures_dict

        assert_equal(type(step_dict), dict)
        assert_equal(len(step_dict), 1)
        assert_in("Step", step_dict)
        assert_equal(type(step_dict["Step"]), Step)

    def test_init_instantiate_all_types(self):
        self.test_time_calculator = TimeCalculator(FILES, all_types=True)
        steps_dict = self.test_time_calculator.PELE_TimeStructures_dict

        assert_equal(type(steps_dict), dict)
        assert_equal(len(steps_dict), 5)
        assert_in("Step", steps_dict)
        assert_equal(type(steps_dict["Step"]), Step)
        assert_in("Perturbation", steps_dict)
        assert_equal(type(steps_dict["Perturbation"]), Perturbation)
        assert_in("ANM", steps_dict)
        assert_equal(type(steps_dict["ANM"]), ANM)
        assert_in("SideChain", steps_dict)
        assert_equal(type(steps_dict["SideChain"]), SideChain)
        assert_in("Minimization", steps_dict)
        assert_equal(type(steps_dict["Minimization"]), Minimization)

    def test_calculate_times_step_type(self):
        self.test_time_calculator = TimeCalculator(FILES, all_types=False)
        self.test_time_calculator.calculate_times()
        step_dict = self.test_time_calculator.PELE_TimeStructures_dict["Step"]

        assert_equal(len(self.test_time_calculator.PELE_TimeStructures_dict), 1)
        assert_equal(step_dict.total_time, 643.229)
        assert_equal(step_dict.occurrences, 6)
        assert_equal(step_dict.lowest_time, 72.389)
        assert_equal(step_dict.lowest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_3.txt")
        assert_equal(step_dict.highest_time, 146.979)
        assert_equal(step_dict.highest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_1.txt")

    # def test_calculate_times_two_types(self): todo: check with only ANM and Perturbation

    def test_calculate_times_all_types(self):
        self.test_time_calculator = TimeCalculator(FILES, all_types=True)
        self.test_time_calculator.calculate_times()
        step_dict = self.test_time_calculator.PELE_TimeStructures_dict["Step"]
        perturbation_dict = self.test_time_calculator.PELE_TimeStructures_dict["Perturbation"]
        anm_dict = self.test_time_calculator.PELE_TimeStructures_dict["ANM"]
        side_chain_dict = self.test_time_calculator.PELE_TimeStructures_dict["SideChain"]
        minimization_dict = self.test_time_calculator.PELE_TimeStructures_dict["Minimization"]

        assert_equal(len(self.test_time_calculator.PELE_TimeStructures_dict), 5)
        self.assert_step(step_dict)
        self.assert_perturbation(perturbation_dict)
        self.assert_anm(anm_dict)
        self.assert_side_chain(side_chain_dict)
        self.assert_minimization(minimization_dict)

    def assert_step(self, step_dict):
        assert_almost_equal(step_dict.total_time, 643.229)
        assert_equal(step_dict.occurrences, 6)
        assert_almost_equal(step_dict.calculate_average(), 107.20483333)
        assert_almost_equal(step_dict.lowest_time, 72.389)
        assert_equal(step_dict.lowest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_3.txt")
        assert_almost_equal(step_dict.highest_time, 146.979)
        assert_equal(step_dict.highest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_1.txt")

    def assert_perturbation(self, perturbation_dict):
        assert_almost_equal(perturbation_dict.total_time, 262.748)
        assert_equal(perturbation_dict.occurrences, 6)
        assert_almost_equal(perturbation_dict.calculate_average(), 43.7913333)
        assert_almost_equal(perturbation_dict.lowest_time, 31.8809)
        assert_equal(perturbation_dict.lowest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_3.txt")
        assert_almost_equal(perturbation_dict.highest_time, 50.7186)
        assert_equal(perturbation_dict.highest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_1.txt")

    def assert_anm(self, anm_dict):
        assert_almost_equal(anm_dict.total_time, 56.1455)
        assert_equal(anm_dict.occurrences, 3)
        assert_almost_equal(anm_dict.calculate_average(), 18.715166666)
        assert_almost_equal(anm_dict.lowest_time, 16.8607)
        assert_equal(anm_dict.lowest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_3.txt")
        assert_almost_equal(anm_dict.highest_time, 21.7559)
        assert_equal(anm_dict.highest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_1.txt")

    def assert_side_chain(self, side_chain_dict):
        assert_almost_equal(side_chain_dict.total_time, 112.3994)
        assert_equal(side_chain_dict.occurrences, 3)
        assert_almost_equal(side_chain_dict.calculate_average(), 37.46646666)
        assert_almost_equal(side_chain_dict.lowest_time, 26.2207)
        assert_equal(side_chain_dict.lowest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_2.txt")
        assert_almost_equal(side_chain_dict.highest_time, 53.6631)
        assert_equal(side_chain_dict.highest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_1.txt")

    def assert_minimization(self, minimization_dict):
        assert_almost_equal(minimization_dict.total_time, 160.8253)
        assert_equal(minimization_dict.occurrences, 6)
        assert_almost_equal(minimization_dict.calculate_average(), 26.80421666)
        assert_almost_equal(minimization_dict.lowest_time, 21.015)
        assert_equal(minimization_dict.lowest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_1.txt")
        assert_almost_equal(minimization_dict.highest_time, 32.5825)
        assert_equal(minimization_dict.highest_time_file_path, "PELETools/TimeCalculator/tests/data/logFile_2.txt")
