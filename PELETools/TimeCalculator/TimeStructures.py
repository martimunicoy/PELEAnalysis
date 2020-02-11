class TimeStructure:

    def __init__(self):
        self._total_time = 0
        self._total_time_variance = 0
        self._occurrences = 0
        self._average = 0
        self._variance = 0
        self._standard_deviation = 0

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

    @property
    def average(self):
        return self._average

    @property
    def variance(self):
        return self._variance

    @property
    def standard_deviation(self):
        return self._standard_deviation

    # Getters
    @total_time.getter
    def total_time(self):
        return self.total_time()

    @total_time_variance.getter
    def total_time_variance(self):
        return self.total_time_variance()

    @occurrences.getter
    def occurrences(self):
        return self.occurrences()

    @average.getter
    def average(self):
        return self.total_time() / self.occurrences()

    @variance.getter
    def variance(self):
        return self.total_time_variance() / self.occurrences()

    @standard_deviation.getter
    def standard_deviation(self):
        return self.standard_deviation()

    # Setters

    @total_time.setter
    def total_time(self, time):
        self.total_time += time

    @total_time_variance.setter
    def total_time_variance(self, variance_time):
        self.total_time_variance += variance_time

    @occurrences.setter
    def occurrences(self, number_of_occurrences):
        self.occurrences += number_of_occurrences
