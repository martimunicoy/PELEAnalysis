# -*- coding: utf-8 -*-


# Imports
import os
import pickle
import numpy as np


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Functions
def isThereAFile(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False


def fromDictValuesToList(input_dict):
    output_list = []
    for key, value in input_dict.items():
        if type(value) is dict:
            value = fromDictValuesToList(value)
        for element in value:
            output_list.append(element)
    return output_list


def unpickle(binary_file):
    with open(binary_file, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def checkFile(file_path):
    file_path = str(file_path)
    if (not os.path.exists(file_path)):
        raise NameError("Invalid path to file: " + file_path)


def normalize(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2 == 0] = 1
    return a / np.expand_dims(l2, axis)


def norm(a, axis=-1, order=2):
    return np.atleast_1d(np.linalg.norm(a, order, axis))