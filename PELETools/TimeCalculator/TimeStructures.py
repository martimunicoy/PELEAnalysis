# Python imports
import sys


class TimeStructure:

    name = ""
    name_to_search_in_log_file = ""
    time_position_in_log_file = 0

    def __init__(self):
        self._total_time = 0
        self._occurrences = 0
        self._lowest_time = sys.float_info.max
        self._lowest_time_file_path = ""
        self._highest_time = sys.float_info.min
        self._highest_time_file_path = ""

    def __str__(self):
        average = 0
        if self.occurrences != 0:
            average = self.calculate_average()
        return "PELE " + self.name + " time: \n" + \
               "---Average time: " + str(average) + "\n" + \
               "---Highest time: " + str(self.highest_time) + "\n" + \
               "---Highest time file path: " + self.highest_time_file_path + "\n" + \
               "---Lowest time: " + str(self.lowest_time) + "\n" + \
               "---Lowest time file path: " + self.lowest_time_file_path + "\n"

    # Properties
    @property
    def total_time(self):
        return self._total_time

    @property
    def occurrences(self):
        return self._occurrences

    @property
    def lowest_time(self):
        return self._lowest_time

    @property
    def highest_time(self):
        return self._highest_time

    @property
    def lowest_time_file_path(self):
        return self._lowest_time_file_path

    @property
    def highest_time_file_path(self):
        return self._highest_time_file_path

    # Setters
    @total_time.setter
    def total_time(self, time):
        self._total_time = time

    @occurrences.setter
    def occurrences(self, number_of_occurrences):
        self._occurrences = number_of_occurrences

    @lowest_time.setter
    def lowest_time(self, time):
        self._lowest_time = time

    @highest_time.setter
    def highest_time(self, time):
        self._highest_time = time

    @lowest_time_file_path.setter
    def lowest_time_file_path(self, path):
        self._lowest_time_file_path = path

    @highest_time_file_path.setter
    def highest_time_file_path(self, path):
        self._highest_time_file_path = path

    # Methods
    def increment_total_time(self, time: float):
        self.total_time += time

    def increment_occurrences(self, number_of_occurrences: int):
        self.occurrences += number_of_occurrences

    def calculate_average(self):
        return self.total_time / self.occurrences
