# -*- coding: utf-8 -*-


# Imports
from __future__ import unicode_literals
import os
import sys
import glob
import argparse as ap
from matplotlib import pyplot
from math import isnan


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Classes
class Simulation:
    def __init__(self, directories, sim_type="PELE", report_name="run_report_",
                 trajectory_name="run_trajectory_", logfile_name="logFile_"):
        self.directories = directories
        self.type = sim_type
        self.report_name = report_name
        self.trajectory_name = trajectory_name
        self.logfile_name = logfile_name
        self.epochs = None
        self.trajectories = None
        self.reports = None

    def initiateCounters(self):
        if self.type is "Adaptive":
            self.epochs = 0

        self.trajectories = 0
        self.models = 0

    def getOutputFiles(self):
        self.initiateCounters()
        self.reports = {}

        if self.type is "Adaptive":
            for directory in self.directories:
                for subdir in glob.glob(directory + "*"):
                    subdir = os.path.basename(subdir)
                    if subdir.isdigit():
                        self.getOutputFilesHere(directory + subdir)
            print("A total of {} epochs and ".format(self.epochs) +
                  "{} reports were found.".format(self.trajectories))

        elif self.type is "PELE":
            for directory in self.directories:
                self.getOutputFilesHere(directory)
            print("A total of {}".format(self.trajectories) +
                  " reports were found.")

    def getOutputFilesHere(self, directory):
        if self.type is "Adaptive":
            self.epochs += 1
            epoch = int(os.path.basename(directory))

        else:
            epoch = None

        self.reports[directory] = []

        for file in glob.glob(directory + "/" + self.report_name + "*"):
            report = Report(directory, os.path.basename(file), self.report_name, epoch=epoch)
            report.setTrajectoryFile(self.trajectory_name)
            report.setLogFile(self.logfile_name)

            self.reports[directory].append(report)
            self.trajectories += 1


class Report:

    def __init__(self, path, name, report_name, epoch=None):
        self.path = path
        self.name = name
        self.epoch = epoch
        self.trajectory_id = int(name.split(report_name)[1].split('.')[-1])
        self.trajectory_file = None
        self.log_file = None

    def setTrajectoryFile(self, trajectory_name):
        name = trajectory_name + str(self.trajectory_id) + ".pdb"
        if os.path.exists(self.path + "/" + name):
            trajectory_file = Trajectory(name, self.path, self, self.epoch,
                                         self.trajectory_id)
            self.trajectory_file = trajectory_file

    def setLogFile(self, logfile_name):
        name = logfile_name + str(self.trajectory_id)
        if os.path.exists(self.path + "/" + name):
            logfile = Logfile(name, self.path, self, self.epoch,
                              self.trajectory_id)
            self.log_file = logfile


class Trajectory:

    def __init__(self, name, path, report_file, epoch, trajectory_id):
        self.name = name
        self.path = path
        self.report_file = report_file
        self.epoch = epoch
        self.trajectory_id = trajectory_id
        self.models = self.getNumberOfModels()

    def getNumberOfModels(self):
        models = 0
        with open(self.path + "/" + self.name) as report_file:
            for line in report_file:
                if line.startswith("MODEL"):
                    models += 1
        return models


class Logfile:

    def __init__(self, name, path, report_file, epoch, trajectory_id):
        self.name = name
        self.path = path
        self.report_file = report_file
        self.epoch = epoch
        self.trajectory_id = trajectory_id


class Atom:
    def __init__(self, chain, residue_id, atom_name):
        self.chain = chain
        self.residue_id = residue_id
        self.atom_name = atom_name


# Functions
def parseReports(reports_to_parse, parser):
    """It identifies the reports to add to the plot

    PARAMETERS
    ----------
    reports_to_parse : list of strings
                       all the report files that want to be added to the plot
    parser : ArgumentParser object
             contains information about the command line arguments

    RETURNS
    -------
    parsed_data : tuple of a list and a string
                  the list specifies the report columns that want to be plotted
                  in the axis and the string sets the name of the axis
    """

    reports = []

    for reports_list in reports_to_parse:
        trajectories_found = glob.glob(reports_list)
        if len(trajectories_found) == 0:
            print("Warning: path to report file \'" +
                  "{}".format(reports_list) + "\' not found.")
        for report in glob.glob(reports_list):
            reports.append(report)

    if len(reports) == 0:
        print("Error: list of report files is empty.")
        parser.print_help()
        exit(1)

    return reports


def parseAtom(atom_to_parse):
    atom_to_parse.strip()
    atom_identifiers = atom_to_parse.split(':')

    try:
        chain, residue_id, atom_name = atom_identifiers
    except ValueError:
        sys.exit("parseAtom: wrong atom format {}".atom_to_parse)

    chain, residue_id, atom_name = atom_identifiers

    atom = Atom(chain, residue_id, atom_name)

    return atom


def parseArgs():
    """Parse arguments from command-line

    RETURNS
    -------
    reports : string
              list of report files to look for data
    x_data : string
             data to parse and assign to the X axis
    y_data : string
             data to parse and assign to the Y axis
    z_data : string
             data to parse and assign to the colorbar
    z_max : float
            it sets the maximum range value of the colorbar
    z_min : float
            it sets the minimum range value of the colorbar
    output_path : string
                  output directory where the resulting plot will be saved
    """

    parser = ap.ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, metavar="FILE",
                          type=str, nargs='*', help="path to simulation files")
    optional.add_argument("-d", "--distance",
                          metavar="CHAIN:ID:ATOM_1 CHAIN:ID:ATOM_2", type=str,
                          nargs='*', help="add distance between two atoms",
                          default=None)
    parser._action_groups.append(optional)
    args = parser.parse_args()

    simulation_dir = parseReports(args.input, parser)

    if args.distance is None or len(args.distance) != 2:
        sys.exit("Two atoms need to be specified to calculate a distance")

    atom1 = parseAtom(args.distance[0])
    atom2 = parseAtom(args.distance[1])

    return simulation_dir, atom1, atom2


def main():
    """Main function

    It is called when this script is the main program called by the interpreter
    """

    # Parse command-line arguments
    simulation_dir, atom1, atom2 = parseArgs()

    simulation = Simulation(simulation_dir, sim_type="Adaptive")

    simulation.getOutputFiles()

    for report in simulation.reports["ARO_ISO_REF/1"]:
        print(report.name, report.epoch, report.trajectory_id, report.trajectory_file.models)


if __name__ == "__main__":
    """Call the main function"""
    main()
