# Repo Imports
import PELETools.TimeCalculator.TimeCalculatorArgParser as argParser
import PELETools.TimeCalculator.ParallelTimeCalculator as parallelCalculator


def main():
    # Parse args
    simulation_path, all_times, jobs, save_path = argParser.parse_arguments()

    result = parallelCalculator.calculate_times(simulation_path, all_times, jobs)

    if save_path != "":
        parallelCalculator.save_results(result, save_path)


if __name__ == "__main__":
    main()

