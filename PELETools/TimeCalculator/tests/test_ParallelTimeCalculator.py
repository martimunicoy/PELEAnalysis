# Project imports
from PELETools.TimeCalculator.ParallelTimeCalculator import calculate_times, save_results

# Libraries imports
from nose.tools import assert_equal, assert_almost_equal, assert_multi_line_equal

# Python imports
import os

TEST_FILES = ["PELETools/TimeCalculator/tests/data/logFile_1.txt",
              "PELETools/TimeCalculator/tests/data/logFile_2.txt",
              "PELETools/TimeCalculator/tests/data/logFile_3.txt"]


class TestParallelTimeCalculator:

    def test_calculate_times_one_job(self):
        result = calculate_times(TEST_FILES, True, 1)
        step_dict = result["Step"]
        perturbation_dict = result["Perturbation"]
        anm_dict = result["ANM"]
        side_chain_dict = result["SideChain"]
        minimization_dict = result["Minimization"]

        assert_equal(len(result), 5)
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

        assert_equal(len(result), 5)
        self.assert_step(step_dict)
        self.assert_perturbation(perturbation_dict)
        self.assert_anm(anm_dict)
        self.assert_side_chain(side_chain_dict)
        self.assert_minimization(minimization_dict)

    def test_save_result(self):
        result = calculate_times(TEST_FILES, True, 1)
        save_results(result, "PELETools/TimeCalculator/tests/data/saveResult")
        save_results(result, "PELETools/TimeCalculator/tests/data/expectedSaveResult")
        with open('PELETools/TimeCalculator/tests/data/saveResult', 'r') as file1:
            with open('PELETools/TimeCalculator/tests/data/expectedSaveResult', 'r') as file2:
                assert_multi_line_equal(file1.read(), file2.read())
                os.remove("PELETools/TimeCalculator/tests/data/saveResult")

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

