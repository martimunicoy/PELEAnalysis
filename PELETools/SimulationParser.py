# -*- coding: utf-8 -*-


# Standard imports
from __future__ import unicode_literals
import os
import glob
import sys
from pathlib import Path


# PELE imports
from . import Plotter
from .Molecules import atomBuilder
from .Molecules import linkBuilder
from .PDB import PDBHandler
from .Utils import fromDictValuesToList, isThereAFile


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Classes
class Epoch(object):
    def __init__(self, path, list_of_reports):
        self._path = Path(path)

        if (not str(self.path.name).isdigit()):
            print('Epoch Warning: epoch\'s path should point to a folder ' +
                  'labeled with an integer. Path is {}'.format(self.path))

        self._reports = list_of_reports

    @property
    def path(self):
        return self._path

    @property
    def reports(self):
        return self._reports

    @property
    def index(self):
        return int(self._path.name)


class EpochBuilder(object):
    def __init__(self, report_name, trajectory_name, logfile_name):
        self.report_name = report_name
        self.trajectory_name = trajectory_name
        self.logfile_name = logfile_name

    def build(self, epoch_directory):
        epoch_directory = Path(epoch_directory)

        list_of_reports = []

        for file in epoch_directory.iterdir():
            if (file.name.startswith(self.report_name)):
                # Get suffix
                suf = file.name[len(self.report_name):]
                # Remove underscore
                suf = suf[1:]
                # Check that suffix is a digit
                if (suf.isdigit()):
                    report = Report(file.absolute(), self)

                    # Build report's trajectory
                    trajectory_path = file.parent.absolute().joinpath(
                        self.trajectory_name + '_' + suf)
                    trajectory = Trajectory(trajectory_path, report)

                    # Build report's logfile
                    logfile_path = file.parent.absolute().joinpath(
                        self.logfile_name + '_' + suf)
                    logfile = Logfile(logfile_path, report)

                    # Set them to the current report instance
                    report.set_trajectory(trajectory)
                    report.set_logfile(logfile)

                    # Add new report to list
                    list_of_reports.append(report)

        return Epoch(epoch_directory, list_of_reports)


class Simulation(object):
    def __init__(self, output_directory, report_name="report_",
                 trajectory_name="trajectory_", logfile_name="logFile_"):
        self._output_directory = Path(output_directory)
        self._report_name = report_name
        self._trajectory_name = trajectory_name
        self._logfile_name = logfile_name
        self._epochs = []
        self.iterateOverReports = None
        self.PDBHandler = PDBHandler(self)

        if (not self.output_directory.exists()):
            print("Simulation Warning: supplied output directory does not " +
                  "exist")

    @property
    def output_directory(self):
        return self._output_directory

    @property
    def report_name(self):
        return self._report_name

    @property
    def trajectory_name(self):
        return self._trajectory_name

    @property
    def logfile_name(self):
        return self._logfile_name

    @property
    def epochs(self):
        return self._epochs

    @property
    def type(self):
        return self._type

    @property
    def n_epochs(self):
        return len(self.epochs)

    @property
    def n_trajectories(self):
        return self._n_trajectories

    @property
    def n_models(self):
        return self._n_models

    def _initiateCounters(self):
        self._n_trajectories = 0
        self._n_models = 0

    def getOutputFiles(self):
        self._scanForOutputFiles()
        self.iterateOverReports = self.reportIterator(self.reports)

    class reportIterator:
        def __init__(self, reports):
            self.reports = fromDictValuesToList(reports)
            self.max_len = len(self.reports)

        def __iter__(self):
            self.current_index = 0
            return self

        def __next__(self):
            if (self.current_index == self.max_len):
                raise StopIteration
            else:
                self.current_index += 1
                return self.reports[self.current_index - 1]

        def __getitem__(self, key):
            for i, report in enumerate(self.reports):
                if (i == key):
                    return report
            raise IndexError

    # @TODO
    def plot(self, plot_type='ScatterPlot'):
        if (plot_type not in Plotter.PLOT_TYPES):
            raise NameError('Unkown plot type \'{}\''.format(plot_type))

        """
        if (plot_type == 'ScatterPlot'):
            plot = Plotter.ScatterPlot(REPORTS!)
        """


class AdaptiveSimulation(Simulation):
    def __init__(self, output_directory, report_name="run_report_",
                 trajectory_name="run_trajectory_", logfile_name="logFile_"):
        self._type = "Adaptive"
        Simulation.__init__(self, output_directory, report_name,
                            trajectory_name, logfile_name)

    def _scanForOutputFiles(self):
        self._initiateCounters()
        self._epochs = []

        epoch_builder = EpochBuilder(self.report_name, self.trajectory_name,
                                     self.logfile_name)

        for subdir in self.output_directory.iterdir():
            if (str(subdir.name).isdigit()):
                epoch = epoch_builder.build(subdir)
                # TODO count the number of trajectories and models of each epoch
                self._epochs.append(epoch)

        print("  - A total of {} epochs and ".format(self.n_epochs) +
              "{} reports were found.".format(self.n_trajectories))


class PELESimulation(Simulation):
    def __init__(self, directories, report_name="run_report_",
                 trajectory_name="run_trajectory_", logfile_name="logFile_"):
        self._type = "PELE"
        Simulation.__init__(self, directories, report_name, trajectory_name,
                            logfile_name)

    def _scanForOutputFiles(self):
        self.initiateCounters()
        self.reports = {}

        for directory in self.directories:
            self.reports[directory] = {}
            self.reports[directory][None] = []
            self._getOutputFilesHere(directory)

        print("  - A total of {} reports were found.".format(
            self.trajectories))

    def _getOutputFilesHere(self, directory):
        path_to_reports = directory

        for file in glob.glob(path_to_reports + '/' + self.report_name + "*"):
            report = Report(path_to_reports, os.path.basename(file),
                            self.report_name, self.PDBHandler)
            report.setTrajectoryFile(self.trajectory_name)
            report.setLogFile(self.logfile_name)

            self.reports[directory][None].append(report)
            self.trajectories += 1


class Report:
    def __init__(self, path, epoch):
        self._path = Path(path)
        self._epoch = epoch
        self._trajectory = None
        self._logfile_name = None
        self.metrics, self.models = self.getReportInfo()

    @property
    def path(self):
        return self._path.absolute()

    @property
    def name(self):
        return self._path.name

    @property
    def epoch(self):
        return self._epoch

    @property
    def id(self):
        return int(self.name.split('_')[-1].split('.')[0])

    @property
    def trajectory(self):
        return self._trajectory

    @property
    def logfile(self):
        return self._logfile

    def set_trajectory(self, trajectory):
        self._trajectory = trajectory

    def set_logfile(self, logfile):
        self._logfile = logfile

    def getReportInfo(self, from_mod=False):
        models = 0

        path_to_report = self.path
        if (from_mod):
            path_to_report = self.path.parent.absolute().joinpath(
                "mod_" + self.path.name)
            if (not path_to_report.is_file()):
                print('SimulationParser.getReportInfo Warning: mod_report ' +
                      'not found, metrics will be retrieved from original ' +
                      'report file.')
                path_to_report = self.path

        with open(path_to_report) as report_file:
            labels = report_file.readline()
            labels = labels.strip()
            label_pairing = {}
            for col, label in enumerate(labels.split("    ")):
                label_pairing[label] = col
            for line in report_file:
                models += 1
        return label_pairing, Models(models)

    def getMetric(self, col_num=None, metric_name=None, from_mod=False):
        if col_num is None and metric_name is None:
            print("Report:getMetric: a column number or a metric name need" +
                  " to be specified to get a metric")
            sys.exit(1)

        path_to_report = self.path + "/" + self.name
        metrics = self.metrics
        if (from_mod):
            if (isThereAFile(self.path + "/mod_" + self.name)):
                path_to_report = self.path + "/mod_" + self.name
                metrics, _ = self.getReportInfo(from_mod=True)
            else:
                print('SimulationParser.getMetric Warning: mod_report not ' +
                      'found, metrics will be retrieved from original ' +
                      'report file.')

        if (col_num is None):
            col_num = metrics[metric_name] + 1

        metric_values = []

        with open(path_to_report) as report_file:
            report_file.readline()
            for i, line in enumerate(report_file):
                if self.models.active[i]:
                    line = line.strip()
                    value = float(line.split("    ")[col_num - 1])
                    metric_values.append(value)

        return metric_values

    def addMetric(self, metric_name, values, try_to_append=False):
        input_report_path = self.path + "/" + self.name
        if (try_to_append):
            if (isThereAFile(self.path + "/mod_" + self.name)):
                input_report_path = self.path + "/mod_" + self.name

        with open(input_report_path) as report_file:
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
    def __init__(self, path, report):
        self._path = Path(path)
        self._report = report

    @property
    def path(self):
        return self._path.absolute()

    @property
    def name(self):
        return self._path.name

    @property
    def report(self):
        return self._report

    @property
    def models(self):
        return self._report.models

    def isAtomThere(self, atom_data):
        _, _, atom_name = atom_data
        atom_name = atom_name.replace("_", " ")
        atom_data[2] = atom_name

        with open(self.path + "/" + self.name) as trajectory_file:
            for i, line in enumerate(trajectory_file):
                if (containsAtom(line, atom_data)):
                    return True
                if (self.PDBHandler is not None):
                    if (i > self.PDBHandler.system_size):
                        break

        return False

    def getAtoms(self, atom_data):
        _, _, atom_name = atom_data
        atom_name = atom_name.replace("_", " ")
        atom_data[2] = atom_name

        if ((self.PDBHandler is not None) and
                (self.PDBHandler.are_atoms_indexed)):
            return self._getAtomsFromIndexedAtoms(atom_data)

        return self._getAtomsFromNonIndexedAtoms(atom_data)

    def _getAtomsFromIndexedAtoms(self, atom_data):
        list_of_atoms = []
        model = 0
        atom_line = self.PDBHandler.getAtomLineInPDB(atom_data)

        with open(self.path + "/" + self.name) as trajectory_file:

            for i, line in enumerate(trajectory_file):
                if (int(i / (self.PDBHandler.system_size + 1)) != model):
                    model += 1

                if (not self.models.active[model]):
                    continue

                current_line = i - (self.PDBHandler.system_size + 1) * model

                if (current_line == atom_line):
                    list_of_atoms.append(atomBuilder(line))

        return list_of_atoms

    def _getAtomsFromNonIndexedAtoms(self, atom_data):
        list_of_atoms = []

        with open(self.path + "/" + self.name) as trajectory_file:
            for line in trajectory_file:
                if containsAtom(line, atom_data):
                    list_of_atoms.append(atomBuilder(line))

        return list_of_atoms

    def isLinkThere(self, link_data):
        if (self.PDBHandler.system_size is None):
            self.PDBHandler.system_size = self.PDBHandler.getSystemSize()

        with open(self.path + "/" + self.name) as trajectory_file:
            if (self.PDBHandler is not None):
                for i, line in enumerate(trajectory_file):
                    if (containsLink(line, link_data)):
                        return True
                    if (i > self.PDBHandler.system_size):
                        break

        return False

    def getLinks(self, link_data):
        if ((self.PDBHandler is not None) and
                (self.PDBHandler.are_atoms_indexed)):
            return self._getLinksFromIndexedAtoms(link_data)

        return self._getLinksFromNonIndexedAtoms(link_data)

    def _getLinksFromIndexedAtoms(self, link_data):
        links_list = []
        lines = \
            self.PDBHandler.getLinkLinesInPDB(link_data).values()

        with open(self.path + "/" + self.name) as trajectory_file:
            list_of_atoms = []
            model = 0
            for i, line in enumerate(trajectory_file):
                if (self.PDBHandler.currentModel(i) != model):
                    if self.models.active[model]:
                        links_list.append(linkBuilder(list_of_atoms))
                        list_of_atoms = []
                    model += 1

                if (not self.models.active[model]):
                    continue

                current_line = i - (self.PDBHandler.system_size + 1) * model

                if (current_line in lines):
                    list_of_atoms.append(atomBuilder(line))

        links_list.append(linkBuilder(list_of_atoms))

        return links_list

    def _getLinksFromNonIndexedAtoms(self, link_data):
        links_list = []

        with open(self.path + "/" + self.name) as trajectory_file:
            list_of_atoms = []
            current_model = 0
            for i, line in enumerate(trajectory_file):
                if (line[:6] == 'ENDMDL'):
                    links_list.append(linkBuilder(list_of_atoms))
                    list_of_atoms = []
                    current_model += 1
                    continue

                if (len(line) < 3):
                    continue

                if (not self.models.active[current_model]):
                    continue

                if (containsLink(line, link_data)):
                    atom = atomBuilder(line)
                    list_of_atoms.append(atom)

        return links_list

    def goToNextModelLine(self, file):
        for i in range(0, self.PDBHandler.getSystemSize()):
            file.readline()
        return file.readline()

    def writeModel(self, model_id, output_path):
        model_out = ""
        with open(self.path + "/" + self.name) as trajectory_file:
            i = int(0)
            line = trajectory_file.readline()
            while(i != int(model_id)):
                line = self.goToNextModelLine(trajectory_file)
                i += 1

            model_out += line

            for i in range(0, self.PDBHandler.getSystemSize()):
                model_out += trajectory_file.readline()

        with open(output_path, 'w') as output_file:
            output_file.write(model_out)


class Logfile:
    def __init__(self, path, report):
        self._path = Path(path)
        self._report = report

    @property
    def path(self):
        return self._path.absolute()

    @property
    def name(self):
        return self._path.name

    @property
    def report(self):
        return self._report


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
    line_residue = int(line[22:26])
    line_atom_name = line[12:16]

    if line_chain == chain:
        if line_residue == residue:
            if line_atom_name == atom_name:
                return True

    return False


def simulationBuilderFromAdaptiveCF(adaptive_cf, pele_cf=None):
    simulation_dir = adaptive_cf.path.parent.joinpath(
        adaptive_cf.data["generalParams"]["outputPath"])

    report_name = None
    trajectory_name = None
    logfile_name = None

    if (pele_cf is not None):
        for command in pele_cf.data["commands"]:
            if command["commandType"] == "peleSimulation":
                report_name = command["PELE_Output"]["reportPath"]
                report_name = report_name.split('/')[-1]
                report_name = report_name.split('.')[0]
                trajectory_name = command["PELE_Output"]["trajectoryPath"]
                trajectory_name = trajectory_name.split('/')[-1]
                trajectory_name = trajectory_name.split('.')[0]
        logfile_name = pele_cf.data["simulationLogPath"]
        logfile_name = logfile_name.split('/')[-1]
        logfile_name = logfile_name.split('.')[0]

    simulation = AdaptiveSimulation(simulation_dir,
                                    report_name=report_name,
                                    trajectory_name=trajectory_name,
                                    logfile_name=logfile_name)
    simulation.getOutputFiles()

    return simulation


def simulationBuilderFromPELECF(pele_cf):
    for command in pele_cf.data["commands"]:
        if command["commandType"] == "peleSimulation":
            simulation_dir = os.path.dirname(pele_cf.path) + '/' + '/'.join(
                command["PELE_Output"]["reportPath"].split('/')[:-1])
            report_name = command["PELE_Output"]["reportPath"]
            report_name = report_name.split('/')[-1]
            report_name = report_name.split('.')[0]
            trajectory_name = command["PELE_Output"]["trajectoryPath"]
            trajectory_name = trajectory_name.split('/')[-1]
            trajectory_name = trajectory_name.split('.')[0]
        logfile_name = pele_cf.data["simulationLogPath"]
        logfile_name = logfile_name.split('/')[-1]
        logfile_name = logfile_name.split('.')[0]

    simulation = PELESimulation(simulation_dir,
                                report_name=report_name,
                                trajectory_name=trajectory_name,
                                logfile_name=logfile_name)
    simulation.getOutputFiles()

    return simulation
