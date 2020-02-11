class Step:

    def __init__(self):
        self._average = 0
        self._variance = 0
        self._standard_deviation = 0

    @property
    def average(self):
        return self._average

    @property
    def variance(self):
        return self._variance

    @property
    def standard_deviation(self):
        return self._standard_deviation

