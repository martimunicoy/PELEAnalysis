# Project imports
from PELETools.TimeCalculator.ParallelTimeCalculator import calculate_times, save_results

# Libraries imports
from nose.tools import assert_equal, assert_almost_equal, assert_multi_line_equal

# Python imports
import os

TEST_FILES = "tests/data/logFile*"


class TestParallelTimeCalculator:

    def test_calculate_times_one_job(self):
        result = calculate_times(TEST_FILES, True, 1)
        step_dict = result["Step"]
        perturbation_dict = result["Perturbation"]
        anm_dict = result["ANM"]
        side_chain_dict = result["SideChain"]
        minimization_dict = result["Minimization"]

        assert_equal(len(result), 6)
        self.assert_step(step_dict)
        self.assert_perturbation(perturbation_dict)
        self.assert_anm(anm_dict)
        self.assert_side_chain(side_chain_dict)
        self.assert_minimization(minimization_dict)

    def test_calculate_times_multiple_jobs(self):
        result = calculate_times(TEST_FILES, True, 3)
        step_dict = result["Step"]
        perturbation_dict = result["Perturbation"]
        anm_dict = result["ANM"]
        side_chain_dict = result["SideChain"]
        minimization_dict = result["Minimization"]

        assert_equal(len(result), 6)
        self.assert_step(step_dict)
        self.assert_perturbation(perturbation_dict)
        self.assert_anm(anm_dict)
        self.assert_side_chain(side_chain_dict)
        self.assert_minimization(minimization_dict)

    def test_save_result(self):
        result = calculate_times(TEST_FILES, True, 1)
        save_results(result, "tests/data/saveResult")
        with open('tests/data/saveResult', 'r') as file1, \
                open('tests/data/expectedSaveResult', 'r') as file2:
            for line1, line2 in zip(file1, file2):
                line1 = line1.rstrip('\r\n')
                line2 = line2.rstrip('\r\n')
                if line1 != line2:
                    return False
            os.remove('tests/data/saveResult')
            return next(file1, None) is None and next(file2, None) is None

    def assert_step(self, step_dict):
        assert_almost_equal(step_dict.total_time, 944.1853)
        assert_equal(step_dict.occurrences, 20)
        assert_almost_equal(step_dict.calculate_average(), 47.209264999999995)
        assert_almost_equal(step_dict.lowest_time, 16.2289)
        assert_equal(step_dict.lowest_time_file_path, "tests/data/logFile_3.txt")
        assert_almost_equal(step_dict.highest_time, 111.653)
        assert_equal(step_dict.highest_time_file_path, "tests/data/logFile_4.txt")

    def assert_perturbation(self, perturbation_dict):
        assert_almost_equal(perturbation_dict.total_time,  81.52741)
        assert_equal(perturbation_dict.occurrences, 20)
        assert_almost_equal(perturbation_dict.calculate_average(), 4.0763705)
        assert_almost_equal(perturbation_dict.lowest_time, 2.84781)
        assert_equal(perturbation_dict.lowest_time_file_path, "tests/data/logFile_2.txt")
        assert_almost_equal(perturbation_dict.highest_time, 6.95409)
        assert_equal(perturbation_dict.highest_time_file_path, "tests/data/logFile_1.txt")

    def assert_water_perturbation(self, water_perturbation_dict):
        assert_almost_equal(water_perturbation_dict.total_time,  81.52741)
        assert_equal(water_perturbation_dict.occurrences, 20)
        assert_almost_equal(water_perturbation_dict.calculate_average(), 4.0763705)
        assert_almost_equal(water_perturbation_dict.lowest_time, 2.84781)
        assert_equal(water_perturbation_dict.lowest_time_file_path,
                     "PELETools/TimeCalculator/tests/data/logFile_2.txt")
        assert_almost_equal(water_perturbation_dict.highest_time, 6.95409)
        assert_equal(water_perturbation_dict.highest_time_file_path,
                     "PELETools/TimeCalculator/tests/data/logFile_1.txt")

    def assert_anm(self, anm_dict):
        assert_almost_equal(anm_dict.total_time, 114.95512000000001)
        assert_equal(anm_dict.occurrences, 12)
        assert_almost_equal(anm_dict.calculate_average(), 9.579593333333333)
        assert_almost_equal(anm_dict.lowest_time, 3.84238)
        assert_equal(anm_dict.lowest_time_file_path, "tests/data/logFile_3.txt")
        assert_almost_equal(anm_dict.highest_time, 21.134)
        assert_equal(anm_dict.highest_time_file_path, "tests/data/logFile_1.txt")

    def assert_side_chain(self, side_chain_dict):
        assert_almost_equal(side_chain_dict.total_time, 62.72581)
        assert_equal(side_chain_dict.occurrences, 12)
        assert_almost_equal(side_chain_dict.calculate_average(), 5.227150833333334)
        assert_almost_equal(side_chain_dict.lowest_time, 2.51079)
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

