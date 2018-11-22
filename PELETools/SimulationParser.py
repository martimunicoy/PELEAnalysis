# -*- coding: utf-8 -*-


# Imports
from __future__ import unicode_literals
import os
import glob
import sys
from PELETools.Molecules import atomBuilder
from PELETools.Molecules import linkBuilder


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
            print("  - A total of {} epochs and ".format(self.epochs) +
                  "{} reports were found.".format(self.trajectories))

        elif self.type is "PELE":
            for directory in self.directories:
                self.getOutputFilesHere(directory)
            print("  - A total of {}".format(self.trajectories) +
                  " reports were found.")

        else:
            print("Wrong Simulation type")
            sys.exit(1)

        if self.epochs == 0 or self.epochs is None:
            trajectories_per_epoch = self.trajectories
        else:
            trajectories_per_epoch = self.trajectories / self.epochs

        self.iterateOverReports = self.reportIterator(self.reports,
                                                      trajectories_per_epoch)

        self.indexed_atoms = self.indexAtoms()

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

    def indexAtoms(self):
        indexedAtoms = {}

        trajectory = self[0].trajectory

        if trajectory.system_size is None:
            trajectory.system_size = trajectory.getSystemSize()

        path = trajectory.path + '/' + trajectory.name

        with open(path) as trajectory_file:
            for i, line in enumerate(trajectory_file):
                if int(i / (self.system_size + 1) > 0):
                    break

                line = line.strip()
                fields = line.split()

                linetype = fields[0]
                chain = fields[4]
                number = fields[5]
                name = fields[2]

                if linetype in ["HETATM", "ATOM"]:
                    if chain in indexedAtoms:
                        if number in indexedAtoms[chain]:
                            if type(indexedAtoms[chain][number]) != dict:
                                indexedAtoms[chain][number] = {}
                            indexedAtoms[chain][number][name] = i
                        else:
                            if type(indexedAtoms[chain]) != dict:
                                indexedAtoms[chain] = {}
                            indexedAtoms[chain][number] = {}
                            indexedAtoms[chain][number][name] = {}

                    try:
                        if type(indexedAtoms[fields[4]]) != dict:
                            indexedAtoms[fields[4]] = {}
                    except KeyError:
                        indexedAtoms[fields[4]] = {}

                    atom_description = fields[4] + ':' + fields[5] + ':' + \
                        fields[2]
                    indexedAtoms[fields[4]]





        return indexedAtoms

    def __getitem__(self, key):
        for i, report in enumerate(self.iterateOverReports):
            if (i == key):
                return report
        raise IndexError

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
        self.trajectory = None
        self.logfile = None
        self.metrics, self.models = self.getReportInfo()

    def setTrajectoryFile(self, trajectory_name):
        name = trajectory_name + str(self.trajectory_id) + ".pdb"
        if os.path.exists(self.path + "/" + name):
            trajectory = Trajectory(name, self.path, self, self.epoch,
                                    self.trajectory_id, self.models)
            self.trajectory = trajectory

    def setLogFile(self, logfile_name):
        name = logfile_name + str(self.trajectory_id)
        if os.path.exists(self.path + "/" + name):
            logfile = Logfile(name, self.path, self, self.epoch,
                              self.trajectory_id)
            self.logfile = logfile

    def getReportInfo(self):
        models = 0
        with open(self.path + "/" + self.name) as report_file:
            labels = report_file.readline()
            labels = labels.strip()
            label_pairing = {}
            for col, label in enumerate(labels.split("    ")):
                label_pairing[label] = col
            for line in report_file:
                models += 1
        return label_pairing, Models(models)

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
            for i, line in enumerate(report_file):
                if self.models.active[i]:
                    line = line.strip()
                    value = float(line.split("    ")[col_num - 1])
                    metric_values.append(value)

        return metric_values

    def addMetric(self, metric_name, values):
        with open(self.path + "/" + self.name) as report_file:
            data = report_file.read()

        lines = data.split("\n")
        new_lines = []

        j = 0

        for i, line in enumerate(lines):
            if i == 0:
                line += "{}    ".format(metric_name)
            elif i <= self.models.number:
                if self.models.active[i - 1]:
                    line += "{0:.4f}    ".format(values[i - 1 - j])
                else:
                    j += 1
            else:
                break
            new_lines.append(line)

        with open(self.path + "/mod_" + self.name, "w") as report_file:
            for line in new_lines:
                report_file.write(line + "\n")


class Trajectory:

    def __init__(self, name, path, report_file, epoch, trajectory_id,
                 models):
        self.name = name
        self.path = path
        self.report_file = report_file
        self.epoch = epoch
        self.trajectory_id = trajectory_id
        self.system_size = None
        self.models = models

    def getSystemSize(self):
        with open(self.path + "/" + self.name) as trajectory_file:
            for size, line in enumerate(trajectory_file):
                if line.startswith("ENDMDL"):
                    break
            return size + 1

    # @TODO: fix bug in self.models.active[1:]
    def getAtoms(self, atom_data):
        if self.system_size is None:
            self.system_size = self.getSystemSize()

        _, _, atom_name = atom_data
        atom_name = atom_name.replace("_", " ")
        atom_data[2] = atom_name

        with open(self.path + "/" + self.name) as trajectory_file:
            atom_matchs = []
            for i, line in enumerate(trajectory_file):
                if containsAtom(line, atom_data):
                    break
                if i > self.system_size:
                    print("Trajectory:getAtoms: atom {}".format(atom_data) +
                          " not found in trajectory {}".format(self.path +
                                                               "/" +
                                                               self.name))
                    return []

            if self.models.active[0]:
                atom_matchs.append(atomBuilder(line, self, 1))

            for model in self.models.active[1:]:
                line = self.goToNextModelLine(trajectory_file)
                if model:
                    atom_matchs.append(atomBuilder(line, self, 1))

            return atom_matchs

    def isLinkThere(self, link_data):
        if self.system_size is None:
            self.system_size = self.getSystemSize()

        with open(self.path + "/" + self.name) as trajectory_file:
            for i, line in enumerate(trajectory_file):
                if containsLink(line, link_data):
                    return True
                if i > self.system_size:
                    break

        return False

    def getLinks(self, link_data):
        if self.system_size is None:
            self.system_size = self.getSystemSize()

        links_list = []

        with open(self.path + "/" + self.name) as trajectory_file:
            list_of_atoms = []
            model = 0
            for i, line in enumerate(trajectory_file):
                if (int(i / (self.system_size + 1)) != model):
                    links_list.append(linkBuilder(list_of_atoms))
                    list_of_atoms = []
                    model += 1

                if not self.models.active[model]:
                    continue

                if containsLink(line, link_data):
                    atom = atomBuilder(line, self, 1)
                    list_of_atoms.append(atom)

        return links_list

    def goToNextModelLine(self, file):
        for i in range(0, self.system_size):
            file.readline()
        return file.readline()


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


class Models:

    def __init__(self, models_number):
        self.number = models_number
        self.active = []
        for i in range(0, self.number):
            self.active.append(True)
        self.current_model = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_model == self.number:
            self.current_model = 0
            raise StopIteration
        else:
            self.current_model += 1
            return self.active[self.current_model - 1]

    def inactivate(self, model_number):
        try:
            self.active[model_number] = False
        except IndexError:
            print("Models:inactivate: model {}".format(model_number) +
                  " could not be deactivated")

    def activate(self, model_number):
        try:
            self.active[model_number] = True
        except IndexError:
            print("Models:activate: model {}".format(model_number) +
                  " could not be activated")

    def activateAll(self):
        for i in range(0, len(self.active)):
            self.active[i] = True

    def deactivateAll(self):
        for i in range(0, len(self.active)):
            self.active[i] = False


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


def containsLink(line, link_data):
    if len(line) < 80:
        return False

    chain, residue = link_data
    residue = int(residue)

    line_chain = line[21]
    line_residue = int(line[23:26])

    if line_chain == chain:
        if line_residue == residue:
            return True

    return False


def containsAtom(line, atom_data):
    if len(line) < 80:
        return False

    chain, residue, atom_name = atom_data
    residue = int(residue)

    line_chain = line[21]
    line_residue = int(line[23:26])
    line_atom_name = line[12:16]

    if line_chain == chain:
        if line_residue == residue:
            if line_atom_name == atom_name:
                return True

    return False
