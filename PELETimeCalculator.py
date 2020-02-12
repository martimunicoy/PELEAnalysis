# Repo Imports
from PELETools.TimeCalculator.TimeCalculatorArgParser import *
from PELETools.TimeCalculator.TimeCalculator import *


def main():
    # Parse args
    simulation_path, all_times, save_path = parse_arguments()

    # Call functions
    time_calculator = TimeCalculator(simulation_path, all_times)
    time_calculator.calculate_times()
    time_calculator.print_times()
    if save_path != "":
        time_calculator.save_results(save_path)


if __name__ == "__main__":
    main()
