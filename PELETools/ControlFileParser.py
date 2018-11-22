# -*- coding: utf-8 -*-


# Imports
import sys
import json
from json import JSONDecodeError
from os.path import dirname


# Classes
class ControlFile(object):
    def __init__(self, path, type=None):
        self.path = path
        self.dir = dirname(path)
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
            except JSONDecodeError:
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


# TO DO
class PELEControlFile(ControlFile):
    def __init__(self, path, type=None):
        self.path = path
        self.data = self.parseJsonFile()
        self.type = self.assignType(type)

    def getPDBs(self):
        PDBs = self.data['Initialization']['MultipleComplex']
        return PDBs


# Functions
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
