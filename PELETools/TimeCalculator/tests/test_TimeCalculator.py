# Project imports
from PELETools.TimeCalculator.TimeCalculator import *

# Libraries imports
from nose.tools import assert_equal, assert_true, assert_in, assert_almost_equal

FILES = ["tests/data/logFile_1.txt",
         "tests/data/logFile_2.txt",
         "tests/data/logFile_3.txt",
         "tests/data/logFile_4.txt"]


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
        assert_equal(len(steps_dict), 6)
        assert_in("Step", steps_dict)
        assert_equal(type(steps_dict["Step"]), Step)
        assert_in("Perturbation", steps_dict)
        assert_equal(type(steps_dict["Perturbation"]), Perturbation)
        assert_in("WaterPerturbation", steps_dict)
        assert_equal(type(steps_dict["WaterPerturbation"]), WaterPerturbation)
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
        assert_almost_equal(step_dict.total_time, 944.1852999999998)
        assert_equal(step_dict.occurrences, 20)
        assert_equal(step_dict.lowest_time, 16.2289)
        assert_equal(step_dict.lowest_time_file_path, "tests/data/logFile_3.txt")
        assert_equal(step_dict.highest_time, 111.653)
        assert_equal(step_dict.highest_time_file_path, "tests/data/logFile_4.txt")

    def test_calculate_times_all_types(self):
        self.test_time_calculator = TimeCalculator(FILES, all_types=True)
        self.test_time_calculator.calculate_times()
        step_dict = self.test_time_calculator.PELE_TimeStructures_dict["Step"]
        perturbation_dict = self.test_time_calculator.PELE_TimeStructures_dict["Perturbation"]
        water_perturbation_dict = self.test_time_calculator.PELE_TimeStructures_dict["WaterPerturbation"]
        anm_dict = self.test_time_calculator.PELE_TimeStructures_dict["ANM"]
        side_chain_dict = self.test_time_calculator.PELE_TimeStructures_dict["SideChain"]
        minimization_dict = self.test_time_calculator.PELE_TimeStructures_dict["Minimization"]

        assert_equal(len(self.test_time_calculator.PELE_TimeStructures_dict), 6)
        self.assert_step(step_dict)
        self.assert_perturbation(perturbation_dict)
        self.assert_water_perturbation(water_perturbation_dict)
        self.assert_anm(anm_dict)
        self.assert_side_chain(side_chain_dict)
        self.assert_minimization(minimization_dict)

    def assert_step(self, step_dict):
        assert_almost_equal(step_dict.total_time, 944.1852999999998)
        assert_equal(step_dict.occurrences, 20)
        assert_almost_equal(step_dict.calculate_average(), 47.20926499999999)
        assert_almost_equal(step_dict.lowest_time, 16.2289)
        assert_equal(step_dict.lowest_time_file_path, "tests/data/logFile_3.txt")
        assert_almost_equal(step_dict.highest_time, 111.653)
        assert_equal(step_dict.highest_time_file_path, "tests/data/logFile_4.txt")

    def assert_perturbation(self, perturbation_dict):
        assert_almost_equal(perturbation_dict.total_time, 81.52741)
        assert_equal(perturbation_dict.occurrences, 20)
        assert_almost_equal(perturbation_dict.calculate_average(), 4.0763705)
        assert_almost_equal(perturbation_dict.lowest_time, 2.84781)
        assert_equal(perturbation_dict.lowest_time_file_path, "tests/data/logFile_2.txt")
        assert_almost_equal(perturbation_dict.highest_time, 6.95409)
        assert_equal(perturbation_dict.highest_time_file_path, "tests/data/logFile_1.txt")

    def assert_water_perturbation(self, water_perturbation_dict):
        assert_almost_equal(water_perturbation_dict.total_time, 60.303149999999995)
        assert_equal(water_perturbation_dict.occurrences, 20)
        assert_almost_equal(water_perturbation_dict.calculate_average(), 3.0151575)
        assert_almost_equal(water_perturbation_dict.lowest_time, 2.69748)
        assert_equal(water_perturbation_dict.lowest_time_file_path, "tests/data/logFile_2.txt")
        assert_almost_equal(water_perturbation_dict.highest_time, 3.6495)
        assert_equal(water_perturbation_dict.highest_time_file_path, "tests/data/logFile_2.txt")

    def assert_anm(self, anm_dict):
        assert_almost_equal(anm_dict.total_time, 114.95512000000002)
        assert_equal(anm_dict.occurrences, 12)
        assert_almost_equal(anm_dict.calculate_average(), 9.579593333333335)
        assert_almost_equal(anm_dict.lowest_time, 3.84238)
        assert_equal(anm_dict.lowest_time_file_path, "tests/data/logFile_3.txt")
        assert_almost_equal(anm_dict.highest_time, 21.134)
        assert_equal(anm_dict.highest_time_file_path, "tests/data/logFile_1.txt")

    def assert_side_chain(self, side_chain_dict):
        assert_almost_equal(side_chain_dict.total_time, 62.72581)
        assert_equal(side_chain_dict.occurrences, 12)
        assert_almost_equal(side_chain_dict.calculate_average(), 5.2271508333333342)
        assert_almost_equal(side_chain_dict.lowest_time,  2.51079)
        assert_equal(side_chain_dict.lowest_time_file_path, "tests/data/logFile_4.txt")
        assert_almost_equal(side_chain_dict.highest_time, 8.20684)
        assert_equal(side_chain_dict.highest_time_file_path, "tests/data/logFile_3.txt")

    def assert_minimization(self, minimization_dict):
        assert_almost_equal(minimization_dict.total_time, 547.267)
        assert_equal(minimization_dict.occurrences, 17)
        assert_almost_equal(minimization_dict.calculate_average(), 32.19217647058824)
        assert_almost_equal(minimization_dict.lowest_time, 11.9417)
        assert_equal(minimization_dict.lowest_time_file_path, "tests/data/logFile_3.txt")
        assert_almost_equal(minimization_dict.highest_time, 89.3784)
        assert_equal(minimization_dict.highest_time_file_path, "tests/data/logFile_4.txt")
