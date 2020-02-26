# Project imports
from PELETools.TimeCalculator.TimeStructures import *

# Libraries imports
from nose.tools import assert_equal


class TestTimeStructure:

    @classmethod
    def setup_class(cls):
        cls.test_time_structure = TimeStructure()

    def setup(self):
        self.test_time_structure.name = "Test"
        self.test_time_structure.total_time = 1
        self.test_time_structure.occurrences = 2
        self.test_time_structure.lowest_time = 3
        self.test_time_structure.lowest_time_file_path = "lowestPath"
        self.test_time_structure.highest_time = 4
        self.test_time_structure.highest_time_file_path = "highestPath"

    def test_init(self):
        assert_equal(self.test_time_structure.name, "Test")
        assert_equal(self.test_time_structure.name_to_search_in_log_file, "")
        assert_equal(self.test_time_structure.time_position_in_log_file, 0)
        assert_equal(self.test_time_structure.total_time, 1)
        assert_equal(self.test_time_structure.occurrences, 2)
        assert_equal(self.test_time_structure.lowest_time, 3)
        assert_equal(self.test_time_structure.lowest_time_file_path, "lowestPath")
        assert_equal(self.test_time_structure.highest_time, 4)
        assert_equal(self.test_time_structure.highest_time_file_path, "highestPath")

    def test_print_report(self):
        string_to_compare = self.test_time_structure.__str__()
        assert_equal(string_to_compare,
                     "PELE Test time: \n"
                     "---Average time: 0.5\n"
                     "---Highest time: 4\n"
                     "---Highest time file path: highestPath\n"
                     "---Lowest time: 3\n"
                     "---Lowest time file path: lowestPath\n")

    def test_increment_total_time(self):
        self.test_time_structure.total_time = 2
        self.test_time_structure.increment_total_time(2)
        assert_equal(self.test_time_structure.total_time, 4)

    def test_increment_occurrences(self):
        self.test_time_structure.occurrences = 2
        self.test_time_structure.increment_occurrences(3)
        assert_equal(self.test_time_structure.occurrences, 5)

    def calculate_average(self):
        self.test_time_structure.total_time = 30
        self.test_time_structure.occurrences = 2
        result = self.test_time_structure.calculate_average()
        assert_equal(result, 15)
