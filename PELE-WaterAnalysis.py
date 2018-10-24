# -*- coding: utf-8 -*-


# Standard imports
import argparse as ap
import sys
import os

# PELE imports
from PELETools.Utils import isThereAFile
from PELETools.ControlFileParser import ControlFile


# Functions
def parseArgs():
    parser = ap.ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-cf", "--controlfile", required=True,
                          metavar="FILE", type=str,
                          help="path to control file")
    parser._action_groups.append(optional)
    args = parser.parse_args()

    cf_path = os.path.abspath(args.controlfile)
    if not isThereAFile(cf_path):
        print("Error: control file not found at \'{}\'".format(cf_path))
        sys.exit(1)

    return cf_path


def main():
    cf_path = parseArgs()
    cf_path
    control_file = ControlFile(cf_path)
    if control_file.type == "Adaptive":
        pcf_path = os.path.dirname(control_file.path) + "/" + \
            control_file.data["simulation"]["params"]["controlFile"]
        pcf_path = os.path.abspath(pcf_path)
        if not isThereAFile(pcf_path):
            print("Error: PELE control file not found at " +
                  "\'{}\'".format(pcf_path))
            sys.exit(1)
        control_file = ControlFile(pcf_path)

    try:
        water_section = control_file.data["commands"][0]["WaterPerturbation"]
    except KeyError:
        print("Error: no WaterPerturbation section was found in PELE " +
              "control file")
        sys.exit(1)

    p_water = water_section["watersToPerturb"]["links"]["ids"]

    if len(p_water) != 1:
        print("Error: only one explicit water molecule should had been "
              "perturbed")
        sys.exit(1)

    p_water = p_water[0]


if __name__ == "__main__":
    main()
