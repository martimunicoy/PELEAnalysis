import argparse as ap
from subprocess import call

from ControlFileParser import ControlFile, PELEControlFile
from ControlFileParser import PELEControlFile, AdaptiveControlFile


def parseArgs():
    """Parse arguments from command-line

    RETURNS
    -------
    controlfile : string
                  path to control file
    """

    parser = ap.ArgumentParser()
    parser.add_argument("-cf", "--controlfile", metavar="FILE",
                        type=str, help="path to control file")

    args = parser.parse_args()

    controlfile = args.controlfile

    return controlfile


def main():

    cf_path = parseArgs()

    controlfile = ControlFile(cf_path)

    if controlfile.type == 'PELE':
        controlfile = PELEControlFile(cf_path)
    else:
        controlfile = AdaptiveControlFile(cf_path)

    simulation_dir = controlfile.path

    print(controlfile.path)
    print(controlfile.getPDBs())

    call(["vmd", "-startup test.txt"])


if __name__ == "__main__":
    """Call the main function"""
    main()
