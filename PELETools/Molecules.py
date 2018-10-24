# -*- coding: utf-8 -*-


# Imports
from __future__ import unicode_literals
import numpy as np


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Classes
class Atom:
    def __init__(self, atom_type, number, atom_name, residue_name, chain,
                 residue_number, coords, element, trajectory, model):
        self.atom_type = atom_type
        self.number = number
        self.atom_name = atom_name
        self.residue_name = residue_name
        self.chain = chain
        self.residue_number = residue_number
        self.coords = coords
        self.element = element
        self.trajectory = trajectory
        self.model = model


def atomBuilder(line, trajectory, model):
    atom_type = line[:6]
    number = line[7:11]
    atom_name = line[12:16]
    residue_name = line[17:20]
    chain = line[21]
    residue_number = line[23:26]
    coords = np.array((float(line[31:38]),
                       float(line[39:46]),
                       float(line[47:54])))
    element = line[76:78]

    atom = Atom(atom_type, number, atom_name, residue_name, chain,
                residue_number, coords, element, trajectory, model)

    return atom
