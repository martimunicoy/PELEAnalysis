# Project imports
from PELETools.TimeCalculator.PELEStepTypes import *

# Python imports
import re
from typing import Dict, List


class TimeCalculator:

    def __init__(self, simulation_path: List, all_types: bool):
        self._simulation_path = simulation_path
        self._PELE_TimeStructures_dict: Dict[str, TimeStructure] = {}

        self._instantiate_objects(all_types)

    @property
    def simulation_path(self):
        return self._simulation_path

    @property
    def PELE_TimeStructures_dict(self):
        return self._PELE_TimeStructures_dict

    def calculate_times(self):
        self._read_file_and_find_times()

    def _instantiate_objects(self, all_types):
        if all_types:
            self._instantiate_PELE_step_types()
        else:
            self._instantiate_only_PELE_step()

    def _read_file_and_find_times(self):
        for file in self._simulation_path:
            with open(file) as opened_file:
                file_lines = opened_file.read().split("\n")
                self._find_matches_and_get_times(file_lines, file)

    def _find_matches_and_get_times(self, file_lines, file_path):
        for line in file_lines:
            for step_type_class in self._PELE_TimeStructures_dict.values():
                if step_type_class.name_to_search_in_log_file in line:
                    time_found = self._find_time_in_line(line, step_type_class)
                    self._compare_upper_lower_times(step_type_class, time_found, file_path)
                    self._increment_variables(time_found, step_type_class)

    def _find_time_in_line(self, line, step_type_class):
        times = re.findall(r"[-+]?\d*\.\d+|\d+", line)
        time_found = float(times[step_type_class.time_position_in_log_file])
        return time_found

    def _compare_upper_lower_times(self, step_type_class: TimeStructure, time_found, file_path):
        if time_found > step_type_class.highest_time:
            step_type_class.highest_time = time_found
            step_type_class.highest_time_file_path = file_path

        if time_found < step_type_class.lowest_time:
            step_type_class.lowest_time = time_found
            step_type_class.lowest_time_file_path = file_path

    def _increment_variables(self, time_found, step_type_class):
        step_type_class.increment_occurrences(1)
        step_type_class.increment_total_time(time_found)

    def _instantiate_PELE_step_types(self):
        for step_name, step_type in PELE_STEP_TYPES_DICT.items():
            self._PELE_TimeStructures_dict[step_name] = step_type()

    def _instantiate_only_PELE_step(self):
        self._PELE_TimeStructures_dict["Step"] = Step()
