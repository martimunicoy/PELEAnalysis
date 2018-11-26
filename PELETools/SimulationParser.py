# -*- coding: utf-8 -*-


# Standard imports
from __future__ import unicode_literals
import os
import glob
import sys


# PELE imports
from PELETools.Molecules import atomBuilder
from PELETools.Molecules import linkBuilder
from PELETools.PDB import PDBHandler
from PELETools.Utils import isThereAFile, fromDictValuesToList


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Classes
class Simulation(object):
    def __init__(self, directories, sim_type="PELE", report_name="run_report_",
                 trajectory_name="run_trajectory_", logfile_name="logFile_",
                 epochs=None, trajectories=None):
        self.directories = directories
        self.type = sim_type
        self.report_name = report_name
        self.trajectory_name = trajectory_name
        self.logfile_name = logfile_name
        self.epochs = epochs
        self.trajectories = trajectories
        self.reports = None
        self.iterateOverReports = None
        self.PDBHandler = None

        if type(self.directories) is not list:
            self.directories = [self.directories, ]

    def initiateCounters(self):
        if self.type is "Adaptive":
            self.epochs = 0

        self.trajectories = 0
        self.models = 0

    # TODO
    def getOutputFiles(self):
        return self.scanForOutputFiles()

    def scanForOutputFiles(self):
        self.initiateCounters()
        self.reports = {}

        if self.type is "Adaptive":
            for directory in self.directories:
                for subdir in glob.glob(directory + "*"):
                    subdir = os.path.basename(subdir)
                    if subdir.isdigit():
                        self._getOutputFilesHere(directory + subdir)
            print("  - A total of {} epochs and ".format(self.epochs) +
                  "{} reports were found.".format(self.trajectories))

        elif self.type is "PELE":
            for directory in self.directories:
                self._getOutputFilesHere(directory)
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

        trajectory = self[0].trajectory
        self.PDBHandler = PDBHandler(trajectory)

    def _getOutputFilesHere(self, directory):
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

    def __getitem__(self, key):
        for i, report in enumerate(self.iterateOverReports):
            if (i == key):
                return report
        raise IndexError

    class reportIterator:
        def __init__(self, reports):
            self.reports = fromDictValuesToList(reports)
            self.current_index = 0
            self.max_len = len(self.reports)

        def __iter__(self):
            return self

        def __next__(self):
            if (self.current_index == self.max_len):
                raise StopIteration
            else:
                self.current_index += 1
                return self.reports[self.current_index - 1]


class AdaptiveSimulation(Simulation):
    def __init__(self, directories, report_name="run_report_",
                 trajectory_name="run_trajectory_", logfile_name="logFile_",
                 epochs=None, trajectories=None):
        self.directories = directories
        self.type = "Adaptive"
        self.report_name = report_name
        self.trajectory_name = trajectory_name
        self.logfile_name = logfile_name
        self.epochs = epochs
        self.trajectories = trajectories
        self.reports = None
        self.iterateOverReports = None
        self.PDBHandler = PDBHandler(self)

        if (type(self.directories) is not list):
            self.directories = [self.directories, ]

    def getOutputFiles(self):
        if (self.epochs is None or self.trajectories is None):
            self.scanForOutputFiles()
        else:
            self.reports = {}
            for directory in self.directories:
                self.reports[directory] = {}
                for epoch in range(0, self.epochs):
                    self.reports[directory][epoch] = []
                    for report_file in [self.report_name + str(i)
                                        for i in range(1, self.trajectories)]:
                        path = directory + str(epoch) + '/' + report_file
                        if (not isThereAFile(path)):
                            print("AdaptiveSimulation:getOutputFiles: " +
                                  "Warning, file: {} ". format(path) +
                                  "not found")
                        else:
                            report = Report(directory + str(epoch),
                                            report_file, self.report_name,
                                            epoch, PDBHandler=self.PDBHandler)
                            report.setTrajectoryFile(self.trajectory_name)
                            report.setLogFile(self.logfile_name)
                            self.reports[directory][epoch].append(report)

        self.iterateOverReports = self.reportIterator(self.reports)

    def scanForOutputFiles(self):
        self.initiateCounters()
        self.reports = {}

        for directory in self.directories:
            self.reports[directory] = {}
            for subdir in glob.glob(directory + "*"):
                subdir = os.path.basename(subdir)
                if (subdir.isdigit()):
                    self.reports[directory][subdir] = []
                    self._getOutputFilesHere(directory + subdir)
        print("  - A total of {} epochs and ".format(self.epochs) +
              "{} reports were found.".format(self.trajectories))

    def _getOutputFilesHere(self, directory):
        self.epochs += 1
        epoch = int(os.path.basename(directory))

        for file in glob.glob(directory + "/" + self.report_name + "*"):
            report = Report(directory, os.path.basename(file),
                            self.report_name, epoch=epoch)
            report.setTrajectoryFile(self.trajectory_name)
            report.setLogFile(self.logfile_name)

            self.reports[directory][epoch].append(report)
            self.trajectories += 1


class Report:

    def __init__(self, path, name, report_name, epoch=None, PDBHandler=None):
        self.path = path
        self.name = name
        self.epoch = epoch
        self.trajectory_id = int(name.split(report_name)[1].split('.')[-1])
        self.trajectory = None
        self.logfile = None
        self.metrics, self.models = self.getReportInfo()
        self.PDBHandler = PDBHandler

    def setTrajectoryFile(self, trajectory_name):
        name = trajectory_name + str(self.trajectory_id) + ".pdb"
        if (not os.path.exists(self.path + "/" + name)):
            print("Report:setTrajectoryFile: Warning, file {} ".format(name) +
                  "not found")
        else:
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
        self.models = models
        self.PDBHandler = self.report_file.PDBHandler

    def isAtomThere(self, atom_data):
        if (self.PDBHandler.system_size is None):
            self.PDBHandler.system_size = self.PDBHandler.getSystemSize()

        _, _, atom_name = atom_data
        atom_name = atom_name.replace("_", " ")
        atom_data[2] = atom_name

        with open(self.path + "/" + self.name) as trajectory_file:
            for i, line in enumerate(trajectory_file):
                if (containsAtom(line, atom_data)):
                    return True
                if (i > self.PDBHandler.system_size):
                    break

        return False

    def getAtoms(self, atom_data):
        if self.PDBHandler is None:
            self.PDBHandler = self.getSystemSize()

        _, _, atom_name = atom_data
        atom_name = atom_name.replace("_", " ")
        atom_data[2] = atom_name

        if ((self.report_file.PDBHandler is not None) and
                (self.report_file.PDBHandler.are_atoms_indexed)):
            return self._getAtomsFromIndexedAtoms(atom_data)
        else:
            return self._getAtomsFromNonIndexedAtoms(atom_data)

    def _getAtomsFromIndexedAtoms(self, atom_data):
        list_of_atoms = []
        model = 0
        atom_line = self.report_file.PDBHandler.getAtomLineInPDB(atom_data)

        with open(self.path + "/" + self.name) as trajectory_file:

            for i, line in enumerate(trajectory_file):
                if (int(i / (self.PDBHandler.system_size + 1)) != model):
                    model += 1

                if (not self.models.active[model]):
                    continue

                current_line = i - (self.PDBHandler.system_size + 1) * model

                if (current_line == atom_line):
                    list_of_atoms.append(atomBuilder(line, self, model))

        return list_of_atoms

    def _getAtomsFromNonIndexedAtoms(self, atom_data):
        list_of_atoms = []
        model = 0

        with open(self.path + "/" + self.name) as trajectory_file:
            for i, line in enumerate(trajectory_file):
                if (int(i / (self.PDBHandler.system_size + 1)) != model):
                    model += 1

                if not self.models.active[model]:
                    continue

                if containsAtom(line, atom_data):
                    list_of_atoms.append(atomBuilder(line, self, 1))

        return list_of_atoms

    def isLinkThere(self, link_data):
        if (self.PDBHandler.system_size is None):
            self.PDBHandler.system_size = self.PDBHandler.getSystemSize()

        with open(self.path + "/" + self.name) as trajectory_file:
            for i, line in enumerate(trajectory_file):
                if (containsLink(line, link_data)):
                    return True
                if (i > self.PDBHandler.system_size):
                    break

        return False

    def getLinks(self, link_data):
        if self.PDBHandler is None:
            self.PDBHandler = self.getSystemSize()

        if ((self.report_file.PDBHandler is not None) and
                (self.report_file.PDBHandler.are_atoms_indexed)):
            return self._getLinksFromIndexedAtoms(link_data)
        else:
            return self._getLinksFromNonIndexedAtoms(link_data)

    def _getLinksFromIndexedAtoms(self, link_data):
        links_list = []
        lines = \
            self.report_file.PDBHandler.getLinkLinesInPDB(link_data).values()

        with open(self.path + "/" + self.name) as trajectory_file:
            list_of_atoms = []
            model = 0
            for i, line in enumerate(trajectory_file):
                if (int(i / (self.PDBHandler.system_size + 1)) != model):
                    links_list.append(linkBuilder(list_of_atoms))
                    list_of_atoms = []
                    model += 1

                if (not self.models.active[model]):
                    continue

                current_line = i - (self.PDBHandler.system_size + 1) * model

                if (current_line in lines):
                    list_of_atoms.append(atomBuilder(line, self, model))

        links_list.append(linkBuilder(list_of_atoms))

        return links_list

    def _getLinksFromNonIndexedAtoms(self, link_data):
        links_list = []

        with open(self.path + "/" + self.name) as trajectory_file:
            list_of_atoms = []
            model = 0
            for i, line in enumerate(trajectory_file):
                if (int(i / (self.PDBHandler.system_size + 1)) != model):
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


def simulationBuilderFromAdaptiveCF(adaptive_cf, pele_cf=None):
    simulation_dir = os.path.dirname(adaptive_cf.path) + '/' + \
        adaptive_cf.data["generalParams"]["outputPath"] + '/'

    epochs = adaptive_cf.data["simulation"]["params"]["iterations"]
    trajectories = adaptive_cf.data["simulation"]["params"]["processors"]

    report_name = None
    trajectory_name = None
    logfile_name = None

    if (pele_cf is not None):
        for command in pele_cf.data["commands"]:
            if command["commandType"] == "peleSimulation":
                report_name = command["PELE_Output"]["reportPath"]
                report_name = report_name.split('/')[-1] + '_'
                trajectory_name = command["PELE_Output"]["trajectoryPath"]
                trajectory_name = trajectory_name.split('/')[-1]
                trajectory_name = trajectory_name.split('.')[0] + '_'
        logfile_name = pele_cf.data["simulationLogPath"]
        logfile_name = logfile_name.split('/')[-1].split('.')[0] + '_'

    simulation = AdaptiveSimulation(simulation_dir, epochs=epochs,
                                    trajectories=trajectories,
                                    report_name=report_name,
                                    trajectory_name=trajectory_name,
                                    logfile_name=logfile_name)
    simulation.getOutputFiles()

    return simulation

