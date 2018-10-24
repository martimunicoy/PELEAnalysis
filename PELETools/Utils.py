# -*- coding: utf-8 -*-


# Imports
import os


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Functions
def isThereAFile(file_path):
    if not os.path.exists(file_path):
        return False
    else:
        return True
