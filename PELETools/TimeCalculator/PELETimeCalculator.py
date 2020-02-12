# Repo Imports
from PELETools.TimeCalculator.TimeCalculatorArgParser import *
from PELETools.TimeCalculator.TimeCalculator import *


def main():
    # Parse args
    output_path, all_times = parse_arguments()

    # Call functions
    time_calculator = TimeCalculator(output_path)
    time_calculator.calculate_step_time()

    if all_times:
        time_calculator.calculate_perturbation_time()
        time_calculator.calculate_ANM_time()
        time_calculator.calculate_side_chain_time()
        time_calculator.calculate_minimization_time()

    # Print/save results
    pass


if __name__ == "__main__":
    main()
