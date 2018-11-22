# -*- coding: utf-8 -*-


# Imports
from __future__ import unicode_literals
import numpy as np
import sys


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


class Link:
    def __init__(self, name, number, list_of_atoms):
        self.name = name
        self.number = number
        self.list_of_atoms = list_of_atoms
        self.iterator_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.iterator_index == len(self.list_of_atoms):
            self.iterator_index = 0
            raise StopIteration
        else:
            self.iterator_index += 1
            return self.list_of_atoms[self.iterator_index - 1]


def linkBuilder(list_of_atoms):
    name = list_of_atoms[0].residue_name
    number = list_of_atoms[0].residue_number

    for atom in list_of_atoms:
        if atom.residue_name != name:
            print("Molecules:linkBuilder: Error, atoms have different " +
                  "residue names and they must belong to the same PDB residue")
            sys.exit(1)
        if atom.residue_number != number:
            print("Molecules:linkBuilder: Error, atoms have different " +
                  "residue numbers and they must belong to the same PDB " +
                  "residue")
            sys.exit(1)

    link = Link(name, number, list_of_atoms)

    return link


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
