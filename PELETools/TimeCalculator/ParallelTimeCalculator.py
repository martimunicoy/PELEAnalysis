# Python imports
from multiprocessing import Process, Queue
import glob

# Repo imports
from PELETools.TimeCalculator.TimeCalculator import *


def calculate_times(simulation_path, all_times, num_jobs) -> Dict[str, TimeStructure]:
    queue: Queue[TimeCalculator] = Queue()
    jobs = []
    simulation_files = _prepare_data(simulation_path, num_jobs)
    for i in range(num_jobs):
        process = Process(target=_launch_jobs, args=(simulation_files[i], all_times, queue))
        jobs.append(process)

    for job in jobs:
        job.start()

    for job in jobs:
        job.join()

    best_results: Dict[str, TimeStructure] = {}
    while not queue.empty():
        _get_best_times(best_results, queue)
    print_results(best_results)

    return best_results


def save_results(best_results, save_path):
    with open(save_path, 'w+') as file:
        for time_structure in best_results.values():
            print(time_structure, file=file)


def print_results(best_results):
    for time_structure in best_results.values():
        print(time_structure)


def _launch_jobs(files_per_job, all_times, queue):
    time_calculator = TimeCalculator(files_per_job, all_times)
    time_calculator.calculate_times()
    queue.put(time_calculator)


def _get_best_times(best_results, queue):
    result = queue.get()
    time_structures_dict: Dict[str, TimeStructure] = result.PELE_TimeStructures_dict

    for time_structure_name, time_structure_object in time_structures_dict.items():
        if time_structure_name not in best_results:
            best_results[time_structure_name] = time_structure_object
        else:
            _actualize_results(time_structure_name, time_structure_object, best_results)


def _actualize_results(time_structure_name, time_structure_object, best_results):
    best_result = best_results[time_structure_name]
    _add_time_and_occurrences(time_structure_object, best_result)
    _compare_lowest_time(time_structure_object, best_result)
    _compare_highest_time(time_structure_object, best_result)


def _compare_lowest_time(time_structure_object, best_result):
    if time_structure_object.lowest_time < best_result.lowest_time:
        best_result.lowest_time = time_structure_object.lowest_time
        best_result.lowest_time_file_path = time_structure_object.lowest_time_file_path


def _compare_highest_time(time_structure_object, best_result):
    if time_structure_object.highest_time > best_result.highest_time:
        best_result.highest_time = time_structure_object.highest_time
        best_result.highest_time_file_path = time_structure_object.highest_time_file_path


def _add_time_and_occurrences(time_structure_object, best_result):
    best_result.total_time += time_structure_object.total_time
    best_result.occurrences += time_structure_object.occurrences


def _prepare_data(simulation_path, jobs):
    file_list = glob.glob(simulation_path)
    return [file_list[i::jobs] for i in range(jobs)]
