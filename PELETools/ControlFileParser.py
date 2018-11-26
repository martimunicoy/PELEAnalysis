# -*- coding: utf-8 -*-


# Standard imports
import sys
import os
import json


# PELE imports
from PELETools.SimulationParser import simulationBuilderFromAdaptiveCF
from PELETools.Utils import isThereAFile


# Classes
class ControlFile(object):
    def __init__(self, path, type=None):
        self.path = path
        self.dir = os.path.dirname(path)
        self.data = self.parseJsonFile()
        self.type = self.assignType(type)

    def assignType(self, type):
        if type is None:
            return identifyControlFileType(self)
        elif type == "PELE":
            return "PELE"
        elif type == "Adaptive":
            return "Adaptive"
        else:
            print("ControlFile.assignType error: unexpected type " +
                  "{}".format(type))
        return type

    def parseJsonFile(self):
        if type(self.path) is not str:
            print("ControlFile.parseJsonFile error: unexpected path" +
                  " to Control File: {}".format(self.path))
            sys.exit(1)
        with open(self.path) as cf:
            try:
                return json.load(cf)
            except json.JSONDecodeError:
                cf.seek(0)
                data = removeAdaptiveSymbolsFromPELEControlFile(cf)
                return json.loads(data)


class AdaptiveControlFile(ControlFile):
    def __init__(self, path, type=None):
        self.path = path
        self.data = self.parseJsonFile()
        self.type = self.assignType(type)

    def getPDBs(self):
        PDBs = self.data['generalParams']['initialStructures']
        return PDBs

    def getPELEControlFile(self):
        pcf_path = os.path.dirname(self.path) + "/" + \
            self.data["simulation"]["params"]["controlFile"]
        pcf_path = os.path.abspath(pcf_path)

        if not isThereAFile(pcf_path):
            print("AdaptiveControlFile:getPELEControlFile: Warning, PELE " +
                  "control file not found")
            return None

        else:
            return PELEControlFile(pcf_path)

    def getSimulation(self):
        pele_cf = self.getPELEControlFile()
        simulation = simulationBuilderFromAdaptiveCF(self, pele_cf)
        return simulation


# TO DO
class PELEControlFile(ControlFile):
    def __init__(self, path, type=None):
        self.path = path
        self.data = self.parseJsonFile()
        self.type = self.assignType(type)

    def getPDBs(self):
        PDBs = self.data['Initialization']['MultipleComplex']
        return PDBs

    def getSimulation(self):
        print("PELEControlFile:getSimulation: not implemented yet")
        return None


# Functions
def getControlFiles(cf_path):
    print(" - Retrieving control files:")

    control_file = ControlFile(cf_path)

    if control_file.type == "Adaptive":
        print("  - Detected Adaptive control file at " +
              "{}".format(control_file.path))
        adaptive_cf = AdaptiveControlFile(cf_path)

        pcf_path = os.path.dirname(adaptive_cf.path) + "/" + \
            adaptive_cf.data["simulation"]["params"]["controlFile"]
        pcf_path = os.path.abspath(pcf_path)

        if not isThereAFile(pcf_path):
            print("Error: PELE control file not found at " +
                  "\'{}\'".format(pcf_path))
            sys.exit(1)

        pele_cf = PELEControlFile(pcf_path)

        print("  - Detected PELE control file at " +
              "{}".format(pele_cf.path))
    else:
        print("  - Detected PELE control file at " +
              "{}".format(control_file.path))
        pele_cf = PELEControlFile(control_file.path)
        adaptive_cf = None

    return adaptive_cf, pele_cf


def identifyControlFileType(controlfile):
    if "generalParams" in controlfile.data:
        return "Adaptive"
    else:
        return "PELE"


def removeAdaptiveSymbolsFromPELEControlFile(cf):
    data = ""
    for line in cf:
        data += line
    data = data.replace("$COMPLEXES", "\"$COMPLEXES\"")
    data = data.replace("$SEED", "\"$SEED\"")
    data = data.replace("$PELE_STEPS", "\"$PELE_STEPS\"")

    return data
