import math


class TimeStructure:

    name = ""
    name_to_search_in_log_file = ""
    time_position_in_log_file = 0

    def __init__(self):
        self._total_time = 0
        self._total_time_variance = 0
        self._occurrences = 0

    def print_report(self):
        print(self)

    # Properties
    @property
    def total_time(self):
        return self._total_time

    @property
    def total_time_variance(self):
        return self._total_time_variance

    @property
    def occurrences(self):
        return self._occurrences

    # Setters
    @total_time.setter
    def total_time(self, time):
        self._total_time = time

    @total_time_variance.setter
    def total_time_variance(self, variance_time):
        self._total_time_variance = variance_time

    @occurrences.setter
    def occurrences(self, number_of_occurrences):
        self._occurrences = number_of_occurrences

    # Methods
    def increment_total_time(self, time):
        self.total_time += time

    def increment_occurrences(self, number_of_occurrences):
        self.occurrences += number_of_occurrences

    def increment_total_time_variance(self, variance_time):
        self.total_time_variance += variance_time

    def calculate_average(self):
        return self.total_time / self.occurrences

    def calculate_variance(self):
        return self.total_time_variance / self.occurrences

    def calculate_standard_deviation(self):
        return math.sqrt(self.total_time_variance)

