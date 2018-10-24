# -*- coding: utf-8 -*-


# Imports
import json
from json import JSONDecodeError


# Classes
class ControlFile:
    def __init__(self, path, type=None):
        self.path = path
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
        with open(self.path) as cf:
            try:
                return json.load(cf)
            except JSONDecodeError:
                cf.seek(0)
                data = removeAdaptiveSymbolsFromPELEControlFile(cf)
                return json.loads(data)


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
