# Python Imports
import argparse as ap


def parse_arguments():
    parser = ap.ArgumentParser()
    __set_required_arguments(parser)
    __set_optional_arguments(parser)
    args = parser.parse_args()

    return args.output_path, args.all_times


def __str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 'True', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'True', 'f', 'n', '0'):
        return False
    else:
        raise ap.ArgumentTypeError('Boolean value expected.')


def __set_required_arguments(argument_parser: ap.ArgumentParser) -> ap.ArgumentParser:
    required_arguments = argument_parser.add_argument_group("Required arguments")
    required_arguments.add_argument("-p", "--output_path", required=True,
                                    metavar="Output Simulation Path", type=str,
                                    help="Output folder of a PELE simulation")

    return argument_parser


def __set_optional_arguments(argument_parser: ap.ArgumentParser) -> ap.ArgumentParser:
    optional_arguments = argument_parser.add_argument_group("Optional arguments")
    optional_arguments.add_argument("-a", "--all_times", required=False, nargs='?',
                                    metavar="Enable calculation of times of a PELE Simulation",
                                    type=__str2bool, const=True, default=False,
                                    help="Activates calculation of all PELE parts")

    return argument_parser
