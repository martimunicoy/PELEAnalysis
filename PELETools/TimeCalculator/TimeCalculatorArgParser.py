# Python Imports
import argparse as ap


def parse_arguments():
    parser = ap.ArgumentParser()
    _set_required_arguments(parser)
    _set_optional_arguments(parser)
    args = parser.parse_args()

    return args.simulation_path, args.all_times, args.jobs, args.output_save


def _set_required_arguments(argument_parser: ap.ArgumentParser) -> ap.ArgumentParser:
    required_arguments = argument_parser.add_argument_group("Required arguments")
    required_arguments.add_argument("-s", "--simulation_path", required=True, nargs='?',
                                    metavar="Simulation Path", type=str,
                                    help="Path to all log files.")

    return argument_parser


def _set_optional_arguments(argument_parser: ap.ArgumentParser) -> ap.ArgumentParser:
    optional_arguments = argument_parser.add_argument_group("Optional arguments")
    optional_arguments.add_argument("-a", "--all_times", required=False, nargs='?',
                                    metavar="Enable calculation of all times of a PELE Simulation",
                                    const=True, default=False,
                                    help="Activates calculation of all PELE parts.")

    optional_arguments.add_argument("-j", "--jobs", required=False, nargs='?',
                                    metavar="Enable multiple processes to calculate times.",
                                    type=int, const=True, default=1,
                                    help="Enable multiple processes to calculate times.")

    optional_arguments.add_argument("-o", "--output_save", required=False, nargs='?',
                                    metavar="Path to save the results of the time calculation", type=str,
                                    const=True, default="",
                                    help="Path to save the results of the time calculation")

    return argument_parser
