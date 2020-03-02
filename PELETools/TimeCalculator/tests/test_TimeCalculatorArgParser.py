# Project imports
from PELETools.TimeCalculator.TimeCalculatorArgParser import *
from nose.tools import assert_equal, assert_raises

# Python imports
from unittest.mock import patch
import sys


class TestTimeCalculatorArgParser:

    def test_parse_arguments_all_arguments(self):
        test_args = ["TestTimeCalculatorArgParser", "-s", "test", "-a", "-j", "4", "-o", "save"]
        with patch.object(sys, 'argv', test_args):
            simulation_path, all_times, jobs, output_save = parse_arguments()
            assert_equal(simulation_path, "test")
            assert_equal(all_times, True)
            assert_equal(jobs, 4)
            assert_equal(output_save, "save")

    def test_parse_arguments_all_arguments_false(self):
        test_args = ["TestTimeCalculatorArgParser", "-s", "test", "-j", "4", "-o", "save"]
        with patch.object(sys, 'argv', test_args):
            simulation_path, all_times, jobs, output_save = parse_arguments()
            assert_equal(simulation_path, "test")
            assert_equal(all_times, False)
            assert_equal(jobs, 4)
            assert_equal(output_save, "save")
