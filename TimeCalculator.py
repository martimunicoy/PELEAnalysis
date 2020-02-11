import glob
import re
import math


class TimeCalculator:

    def __init__(self, output_simulation_path):
        self._output_simulation_path = output_simulation_path

    @property
    def output_simulation_path(self):
        return self._output_simulation_path

    def calculate_step_time(self):
        occurrences, file_time, variance_file_time = self.__calculate_times_for_step()
        avg_file_time, final_variance_file_time = self.__perform_operations(file_time, occurrences,
                                                                            variance_file_time)
        self.__print_results("step", avg_file_time, final_variance_file_time)

    def calculate_perturbation_time(self):
        occurrences, file_time, variance_file_time = self.__calculate_times_for_perturbation()
        avg_file_time, final_variance_file_time = self.__perform_operations(file_time, occurrences,
                                                                            variance_file_time)
        self.__print_results("Perturbation", avg_file_time, final_variance_file_time)

    def calculate_ANM_time(self):
        occurrences, file_time, variance_file_time = self.__calculate_times_for_ANM()
        avg_file_time, final_variance_file_time = self.__perform_operations(file_time, occurrences,
                                                                            variance_file_time)
        self.__print_results("ANM", avg_file_time, final_variance_file_time)

    def calculate_side_chain_time(self):
        occurrences, file_time, variance_file_time = self.__calculate_times_for_side_chain()
        avg_file_time, final_variance_file_time = self.__perform_operations(file_time, occurrences,
                                                                            variance_file_time)
        self.__print_results("Side Chain", avg_file_time, final_variance_file_time)

    def calculate_minimization_time(self):
        occurrences, file_time, variance_file_time = self.__calculate_times_for_minimization()
        avg_file_time, final_variance_file_time = self.__perform_operations(file_time, occurrences,
                                                                            variance_file_time)
        self.__print_results("Minimization", avg_file_time, final_variance_file_time)

    def __calculate_times_for_step(self):
        occurrences, file_time, variance_file_time = 0, 0, 0
        file_list = glob.glob(self._output_simulation_path)
        for file in file_list:
            with open(file) as opened_file:
                file_lines = opened_file.read().split("\n")
                occurrences, file_time, variance_file_time = \
                    self.__iterate_through_step_lines(file_lines, occurrences, file_time, variance_file_time)

        return occurrences, file_time, variance_file_time

    def __calculate_times_for_perturbation(self):
        occurrences, file_time, variance_file_time = 0, 0, 0
        file_list = glob.glob(self._output_simulation_path)
        for file in file_list:
            with open(file) as opened_file:
                file_lines = opened_file.read().split("\n")
                occurrences, file_time, variance_file_time = \
                    self.__iterate_through_algorithm_lines(
                        "Perturbation Ef:", file_lines, occurrences, file_time, variance_file_time
                    )

        return occurrences, file_time, variance_file_time

    def __calculate_times_for_ANM(self):
        occurrences, file_time, variance_file_time = 0, 0, 0
        file_list = glob.glob(self._output_simulation_path)
        for file in file_list:
            with open(file) as opened_file:
                file_lines = opened_file.read().split("\n")
                occurrences, file_time, variance_file_time = \
                    self.__iterate_through_algorithm_lines(
                        "ANM Ef:", file_lines, occurrences, file_time, variance_file_time
                    )

        return occurrences, file_time, variance_file_time

    def __calculate_times_for_side_chain(self):
        occurrences, file_time, variance_file_time = 0, 0, 0
        file_list = glob.glob(self._output_simulation_path)
        for file in file_list:
            with open(file) as opened_file:
                file_lines = opened_file.read().split("\n")
                occurrences, file_time, variance_file_time = \
                    self.__iterate_through_algorithm_lines(
                        "Side Chain Prediction Ef:", file_lines, occurrences, file_time, variance_file_time
                    )

        return occurrences, file_time, variance_file_time

    def __calculate_times_for_minimization(self):
        occurrences, file_time, variance_file_time = 0, 0, 0
        file_list = glob.glob(self._output_simulation_path)
        for file in file_list:
            with open(file) as opened_file:
                file_lines = opened_file.read().split("\n")
                occurrences, file_time, variance_file_time = \
                    self.__iterate_through_algorithm_lines(
                        "Minimization Ef:", file_lines, occurrences, file_time, variance_file_time
                    )

        return occurrences, file_time, variance_file_time

    def __iterate_through_step_lines(self, file_lines, occurrences, file_time, variance_file_time):
        for line in file_lines:
            if "step time" in line:
                occurrences += 1
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                file_time += float(numbers[0])
                variance_file_time += float(numbers[0]) ** 2

        return occurrences, file_time, variance_file_time

    def __perform_operations(self, file_time, occurrences, variance_file_time):

        average_file_time = file_time / occurrences
        final_variance_file_time = variance_file_time / occurrences

        return average_file_time, final_variance_file_time

    def __iterate_through_algorithm_lines(self, algorithm_type, file_lines, occurrences, file_time, variance_file_time):
        for line in file_lines:
            if algorithm_type in line:
                occurrences += 1
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                file_time += float(numbers[-1])
                variance_file_time += float(numbers[-1]) ** 2

        return occurrences, file_time, variance_file_time

    def __print_results(self, result_type, average_file_time, final_variance_file_time):
        print("Results of " + result_type + " calculation...")
        print("---Average time: " + str(average_file_time))
        print("---Variance time: " + str(final_variance_file_time))
        print("---Standard Deviation: " + str(math.sqrt(final_variance_file_time)) + "\n")
