# -*- coding: utf-8 -*-


# Standard imports
import argparse as ap
import sys
import os
from array import array


# PELE imports
from PELETools.Utils import isThereAFile
from PELETools.ControlFileParser import getControlFiles


# Constants
WATER_ATOMS = ("_OW_", "1HW_", "2HW_")


# Functions
def parseArgs():
    parser = ap.ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional.add_argument("-cf", "--controlfile", required=False,
                          metavar="FILE", type=str,
                          help="path to Adaptive PELE control file")
    optional.add_argument("-bc", "--binarycoords", required=False,
                          metavar="FILE", type=str,
                          help="path to binary coords file")
    parser._action_groups.append(optional)
    args = parser.parse_args()

    if args.controlfile is not None:
        cf_path = os.path.abspath(args.controlfile)
        if not isThereAFile(cf_path):
            print("Error: controlfile not found at \'{}\'".format(cf_path))
            sys.exit(1)
    else:
        cf_path = None

    if args.binarycoords is not None:
        bc_path = os.path.abspath(args.binarycoords)
        if not isThereAFile(bc_path):
            print("Error: binarycoords file not found at " +
                  "\'{}\'".format(bc_path))
            sys.exit(1)
    else:
        bc_path = None

    return cf_path, bc_path


def getPerturbedWater(pele_cf):
    print(" - Looking for the perturbed water molecule:")

    try:
        water_section = \
            pele_cf.data["commands"][0]["WaterPerturbation"]
    except KeyError:
        print("Error: no WaterPerturbation section was found in PELE " +
              "control file")
        sys.exit(1)

    p_water = water_section["watersToPerturb"]["links"]["ids"]

    if len(p_water) != 1:
        print("Error: detected more than one perturbed water " +
              "molecule, only one explicit water molecule should " +
              "had been perturbed")
        sys.exit(1)

    p_water = p_water[0]

    print("  - Found water {}".format(p_water))

    return p_water


def parseSimulation(control_file):
    print(" - Parsing simulation")
    simulation = control_file.getSimulation()

    print(" - Indexing simulation atoms")
    simulation.PDBHandler.indexAtoms()

    return simulation


def deactivateFirstModels(simulation):
    print(" - First models are deactivated")

    for report in simulation.iterateOverReports:
        report.trajectory.models.inactivate(0)

    simulation[0].trajectory.models.activate(0)


def getWaterCoords(simulation, p_water):
    print(" - Retrieving water {} coordinates from \'{}\'".format(p_water,
          simulation.directories[0]))

    chain, atom_id = p_water.split(':')
    atom_id = int(atom_id)
    link_data = [chain, atom_id]

    water_coords = []

    if not simulation[0].trajectory.isLinkThere(link_data):
        print("Error: link {} not found in trajectory ".format(link_data) +
              "{}".format(simulation.trajectories[0].path))
        sys.exit(1)

    for report in simulation.iterateOverReports:
        for link in report.trajectory.getLinks(link_data):
            for atom in link:
                for coord in atom.coords.tolist():
                    water_coords.append(coord)

    print("  - Retrieved {} water coordinates".format(len(water_coords)))

    return water_coords


def saveBinaryCoordsFile(water_coords, output_file='coords.bin'):
    print(" - Saving water coordinates to \'{}\'".format(output_file))

    with open(output_file, 'wb') as f:
        float_array = array('d', water_coords)
        float_array.tofile(f)

    print("  - Saved \'{}\'".format(output_file))

    return output_file


def readBinaryCoordsFile(binary_file):
    print(" - Reading water coordinates from \'{}\'".format(binary_file))

    with open(binary_file, 'rb') as f:
        water_coords = array('d')
        water_coords.fromstring(f.read())

    print("  - Obtained \'{}\' water coordinates".format(len(water_coords)))

    return water_coords


def main(cf_path=None, bc_path=None):
    if ((cf_path is None) and (bc_path is None)):
        print(" +-----------------------------------------+")
        print(" | Water Analysis Script for Adaptive PELE |")
        print(" +-----------------------------------------+")
        print(" ")

        cf_path, bc_path = parseArgs()

    if bc_path is not None:
        print(" - Input binarycoords file \'{}\' will be ".format(bc_path) +
              "used to retrieve coordinates from the perturbed water "
              "molecule")

        water_coords = readBinaryCoordsFile(bc_path)

    elif cf_path is not None:
        print(" - Input controlfile \'{}\' will be used to ".format(cf_path) +
              "retrieve coordinates from the perturbed water molecule and " +
              "they will be saved in a binarycoord file " +
              "\'{}\'".format('coords.bin'))

        adaptive_cf, pele_cf = getControlFiles(cf_path)

        if adaptive_cf is None:
            print("Error: this script is only compatible with Adaptive PELE "
                  "and no Adaptive PELE controlfile has been detected.")
            sys.exit(1)

        p_water = getPerturbedWater(pele_cf)

        simulation = parseSimulation(adaptive_cf)

        deactivateFirstModels(simulation)

        water_coords = getWaterCoords(simulation, p_water)

        bc_path = saveBinaryCoordsFile(water_coords)

        main(bc_path=bc_path)

    else:
        print(" - Nothing to do")

    """
    with open('coords.bin', 'rb') as f:
        float_array = array('d')
        float_array.fromstring(f.read())
    """


if __name__ == "__main__":
    main()
