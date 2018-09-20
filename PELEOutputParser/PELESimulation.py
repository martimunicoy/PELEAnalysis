# -*- coding: utf-8 -*-


# Imports
from __future__ import unicode_literals
import os
import glob
import sys


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
        self.iterateOverReports = None

        if type(self.directories) is not list:
            self.directories = [self.directories, ]

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

        self.iterateOverReports = self.reportIterator(self.reports,
                                                      self.trajectories /
                                                      self.epochs)

    def getOutputFilesHere(self, directory):
        if self.type is "Adaptive":
            self.epochs += 1
            epoch = int(os.path.basename(directory))

        else:
            epoch = None

        self.reports[directory] = []

        for file in glob.glob(directory + "/" + self.report_name + "*"):
            report = Report(directory, os.path.basename(file),
                            self.report_name, epoch=epoch)
            report.setTrajectoryFile(self.trajectory_name)
            report.setLogFile(self.logfile_name)

            self.reports[directory].append(report)
            self.trajectories += 1

    class reportIterator:
        def __init__(self, reports, trajs):
            self.reports = reports
            self.current_dir = 0
            self.dirs = list(reports.keys())
            self.current_traj = 0
            self.trajs = trajs

        def __iter__(self):
            return self

        def __next__(self):
            if self.current_dir == len(self.dirs):
                raise StopIteration
            else:
                if self.current_traj == self.trajs:
                    self.current_dir += 1
                    self.current_traj = 0
                    return self.__next__()
                else:
                    directory = self.dirs[self.current_dir]
                    self.current_traj += 1
                    return self.reports[directory][self.current_traj - 1]


class Report:

    def __init__(self, path, name, report_name, epoch=None):
        self.path = path
        self.name = name
        self.epoch = epoch
        self.trajectory_id = int(name.split(report_name)[1].split('.')[-1])
        self.trajectory_file = None
        self.log_file = None
        self.metrics, self.models = self.getReportInfo()

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

    def getReportInfo(self):
        models = 0
        with open(self.path + "/" + self.name) as report_file:
            labels = report_file.readline()
            labels = labels.strip()
            label_pairing = {}
            for col, label in enumerate(labels.split("    ")):
                label_pairing[label] = col + 1
            for line in report_file:
                models += 1
        return label_pairing, models

    def getMetric(self, col_num=None, metric_name=None):
        if col_num is None and metric_name is None:
            print("Report:getMetric: a column number or a metric name need" +
                  " to be specified to get a metric")
            sys.exit(1)
        elif col_num is None:
            col_num = self.metrics[metric_name]

        metric_values = []

        with open(self.path + "/" + self.name) as report_file:
            report_file.readline()
            for line in report_file:
                line = line.strip()
                value = float(line.split("    ")[col_num - 1])
                metric_values.append(value)

        return metric_values


class Trajectory:

    def __init__(self, name, path, report_file, epoch, trajectory_id):
        self.name = name
        self.path = path
        self.report_file = report_file
        self.epoch = epoch
        self.trajectory_id = trajectory_id
        self.models = None


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
