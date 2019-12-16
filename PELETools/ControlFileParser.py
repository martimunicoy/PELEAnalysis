# -*- coding: utf-8 -*-


# Standard imports
import os
import json
from pathlib import Path


# PELE imports
from .SimulationParser import simulationBuilderFromAdaptiveCF
from .SimulationParser import simulationBuilderFromPELECF


# Classes
class ControlFileBuilder(object):
    def __init__(self, path_to_report):
        self._path_to_report = str(path_to_report)

    @property
    def path_to_report(self):
        return self._path_to_report

    def build(self):
        data = self._parseJsonFile()
        control_file_type = self._identifyControlFileType(data)

        if (control_file_type == 'Adaptive'):
            return AdaptiveControlFile(self.path_to_report, data)
        elif (control_file_type == 'PELE'):
            return PELEControlFile(self.path_to_report, data)

    def _parseJsonFile(self):
        try:
            with open(self.path_to_report) as cf:
                try:
                    return json.load(cf)
                except json.JSONDecodeError:
                    cf.seek(0)
                    data = removeAdaptiveSymbolsFromPELEControlFile(cf)
                    return json.loads(data)

        except FileNotFoundError:
            raise NameError("Invalid control file path: \'{}\'".format(
                self._path_to_report))

    def _identifyControlFileType(self, data):
        if ('generalParams' in data):
            return 'Adaptive'
        elif ('Initialization' in data):
            return "PELE"
        else:
            raise NameError('Control file type not recognized: \'{}\''.format(
                self.path))


class ControlFile(object):
    def __init__(self, path, data):
        self._path = Path(path)
        self._dir = os.path.dirname(path)
        self._data = data

    @property
    def path(self):
        return self._path

    @property
    def dir(self):
        return self._dir

    @property
    def data(self):
        return self._data

    @property
    def type(self):
        return self._type


class AdaptiveControlFile(ControlFile):
    def __init__(self, path, data):
        self._type = "Adaptive"
        ControlFile.__init__(self, path, data)

    def getPDBs(self):
        PDBs = self.data['generalParams']['initialStructures']
        return PDBs

    def getPELEControlFile(self):
        pcf_path = self.path.parent.joinpath(
            self.data["simulation"]["params"]["controlFile"])

        if (not pcf_path.is_file()):
            print("AdaptiveControlFile:getPELEControlFile: Warning, PELE " +
                  "control file not found")
            return None

        else:
            builder = ControlFileBuilder(str(pcf_path.absolute()))
            return builder.build()

    def getSimulation(self):
        pele_cf = self.getPELEControlFile()
        simulation = simulationBuilderFromAdaptiveCF(self, pele_cf)
        return simulation


class PELEControlFile(ControlFile):
    def __init__(self, path, data):
        self._type = "PELE"
        ControlFile.__init__(self, path, data)

    def getPDBs(self):
        PDBs = self.data['Initialization']['MultipleComplex']
        return PDBs

    def getSimulation(self):
        simulation = simulationBuilderFromPELECF(self)
        return simulation


# Functions
def removeAdaptiveSymbolsFromPELEControlFile(cf):
    data = ""
    for line in cf:
        data += line
    data = data.replace("$COMPLEXES", "\"$COMPLEXES\"")
    data = data.replace("$SEED", "\"$SEED\"")
    data = data.replace("$PELE_STEPS", "\"$PELE_STEPS\"")

    return data
