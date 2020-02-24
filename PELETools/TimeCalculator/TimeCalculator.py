# Repo imports
from PELETools.TimeCalculator.PELEStepTypes import *

# Python imports
import re
from typing import Dict


class TimeCalculator:

    def __init__(self, simulation_path, all_types):
        self._simulation_path = simulation_path
        self._PELE_TimeStructures_dict: Dict[str, TimeStructure] = {}

        self.__instantiate_objects(all_types)

    @property
    def PELE_TimeStructures_dict(self):
        return self._PELE_TimeStructures_dict

    @PELE_TimeStructures_dict.setter
    def PELE_TimeStructures_dict(self, step_dict):
        self._PELE_TimeStructures_dict = step_dict

    def calculate_times(self):
        self.__read_file_and_find_times()

    def print_times(self):
        for step_type_class in self._PELE_TimeStructures_dict.values():
            print(step_type_class)

    def __instantiate_objects(self, all_types):
        if all_types:
            self.__instantiate_PELE_step_types()
        else:
            self.__instantiate_only_PELE_step()

    def __read_file_and_find_times(self):
        for file in self._simulation_path:
            with open(file) as opened_file:
                file_lines = opened_file.read().split("\n")
                self.__find_matches_and_get_times(file_lines, file)

    def __find_matches_and_get_times(self, file_lines, file_path):
        for line in file_lines:
            for step_type_class in self._PELE_TimeStructures_dict.values():
                if step_type_class.name_to_search_in_log_file in line:
                    time_found = self.__find_time_in_line(line, step_type_class)
                    self.__compare_upper_lower_times(step_type_class, time_found, file_path)
                    self.__increment_variables(time_found, step_type_class)

    def __find_time_in_line(self, line, step_type_class):
        times = re.findall(r"[-+]?\d*\.\d+|\d+", line)
        time_found = float(times[step_type_class.time_position_in_log_file])
        return time_found

    def __compare_upper_lower_times(self, step_type_class: TimeStructure, time_found, file_path):
        if time_found > step_type_class.highest_time:
            step_type_class.highest_time = time_found
            step_type_class.highest_time_file_path = file_path

        if time_found < step_type_class.lowest_time:
            step_type_class.lowest_time = time_found
            step_type_class.lowest_time_file_path = file_path

    def __increment_variables(self, time_found, step_type_class):
        step_type_class.increment_occurrences(1)
        step_type_class.increment_total_time(time_found)

    def __instantiate_PELE_step_types(self):
        for step_name, step_type in PELE_STEP_TYPES_DICT.items():
            self._PELE_TimeStructures_dict[step_name] = step_type()

    def __instantiate_only_PELE_step(self):
        self._PELE_TimeStructures_dict["Step"] = Step()
