# -*- coding: utf-8 -*-


# Python imports
from __future__ import unicode_literals
import numpy as np
import sys


# FEP_PELE imports
from .Utils import norm


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Classes
class Atom:
    def __init__(self, atom_type, number, atom_name, alt_loc, residue_name,
                 chain, residue_number, i_code, coords, occupancy, tempFactor,
                 element, charge):
        self._atom_type = atom_type
        self._number = number
        self._atom_name = atom_name
        self._alt_loc = alt_loc
        self._residue_name = residue_name
        self._chain = chain
        self._residue_number = residue_number
        self._i_code = i_code
        self._coords = coords
        self._occupancy = occupancy
        self._tempFactor = tempFactor
        self._element = element
        self._charge = charge
        self._is_heteroatom = False

    @property
    def atom_type(self):
        return self._atom_type

    @property
    def number(self):
        return self._number

    @property
    def atom_name(self):
        return self._atom_name

    @property
    def alt_loc(self):
        return self._alt_loc

    @property
    def residue_name(self):
        return self._residue_name

    @property
    def chain(self):
        return self._chain

    @property
    def residue_number(self):
        return self._residue_number

    @property
    def i_code(self):
        return self._i_code

    @property
    def coords(self):
        return self._coords

    @property
    def occupancy(self):
        return self._occupancy

    @property
    def tempFactor(self):
        return self._tempFactor

    @property
    def element(self):
        return self._element

    @property
    def charge(self):
        return self._charge

    @property
    def is_heteroatom(self):
        return self._is_heteroatom

    def __lt__(self, other):
        if (self.chain == other.chain):
            if (self.residue_number == other.residue_number):
                return bool(self.number < other.number)
            else:
                return bool(self.residue_number < other.residue_number)
        else:
            return bool(self.chain < other.chain)

    def __eq__(self, other):
        return bool((self.chain, self.residue_number, self.number) ==
                    (other.chain, other.residue_number, other.number))

    def __ne__(self, other):
        return not(self == other)

    def __hash__(self):
        return hash((self.chain, self.residue_number, self.number))

    def __str__(self):
        return str(self.chain) + ':' + str(self.residue_number) + ':' + \
            str(self.atom_name)

    def setAsHeteroatom(self):
        self._is_heteroatom = True

    def setNewCoords(self, coords):
        self._coords = np.array(coords)

    def calculateDistanceWith(self, other):
        return np.abs(norm(self.coords - other.coords))


class Link:
    def __init__(self, name, number, chain, list_of_atoms):
        self.name = name
        self.number = number
        self.chain = chain
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

    def __lt__(self, other):
        if (self.chain == other.chain):
                return self.number < other.number
        else:
            return bool(self.chain < other.chain)

    def __eq__(self, other):
        return bool((self.chain, self.number) ==
                    (other.chain, other.number))

    def __ne__(self, other):
        return not(self == other)

    def getAtomWithName(self, atom_name):
        atom_name = atom_name.replace(' ', '_')

        for atom in self.list_of_atoms:
            if (atom.atom_name == atom_name):
                return atom

    def calculateRMSDWith(self, other):
        atoms1 = sorted(self.list_of_atoms)
        atoms2 = sorted(other.list_of_atoms)
        if (atoms1 != atoms2):
            raise TypeError("The two links must contain the same atoms")

        rmsd = np.sqrt(np.mean(np.square(
            [coord1 - coord2 for atom1, atom2 in zip(atoms1, atoms2)
             for coord1, coord2 in zip(atom1.coords, atom2.coords)])))

        return rmsd


class Chain:
    def __init__(self, name, list_of_links):
        self.name = name
        self.list_of_links = list_of_links
        self.iterator_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.iterator_index == len(self.list_of_links):
            self.iterator_index = 0
            raise StopIteration
        else:
            self.iterator_index += 1
            return self.list_of_links[self.iterator_index - 1]

    def __lt__(self, other):
        return bool(self.name < other.name)

    def __eq__(self, other):
        return bool(self.name == other.name)

    def __ne__(self, other):
        return not(self == other)


class Model:
    def __init__(self, list_of_chains, model_number):
        self._list_of_chains = list_of_chains
        self._model_number = int(model_number)
        self.iterator_index = 0

    @property
    def chains(self):
        return self._list_of_chains

    @property
    def number(self):
        return self._model_number

    def __iter__(self):
        return self

    def __next__(self):
        if self.iterator_index == len(self.chains):
            self.iterator_index = 0
            raise StopIteration
        else:
            self.iterator_index += 1
            return self.chains[self.iterator_index - 1]

    def __lt__(self, other):
        return bool(self.number < other.number)

    def __eq__(self, other):
        return bool(self.number == other.number)

    def __ne__(self, other):
        return not(self == other)


def chainBuilder(list_of_links):
    if ((type(list_of_links) != list) and
            (type(list_of_links) != tuple)):
        print("Molecules:chainBuilder: Error, invalid list of links")
        sys.exit(1)

    if (len(list_of_links) == 0):
        print("Molecules:chainBuilder: Error, empty list of links")
        sys.exit(1)

    name = list_of_links[0].chain

    for link in list_of_links:
        if link.chain != name:
            print("Molecules:chainBuilder: Error, links have different " +
                  "chain ids and they must belong to the same PDB chain")
            sys.exit(1)

    chain = Chain(name, list_of_links)

    return chain


def linkBuilder(list_of_atoms):
    if ((type(list_of_atoms) != list) and
            (type(list_of_atoms) != tuple)):
        print("Molecules:linkBuilder: Error, invalid list of atoms")
        sys.exit(1)

    if (len(list_of_atoms) == 0):
        print("Molecules:linkBuilder: Error, empty list of atoms")
        sys.exit(1)

    name = list_of_atoms[0].residue_name
    number = list_of_atoms[0].residue_number
    chain = list_of_atoms[0].chain

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
        if atom.chain != chain:
            print("Molecules:linkBuilder: Error, atoms have different " +
                  "chain ids and they must belong to the same PDB residue")
            sys.exit(1)

    link = Link(name, number, chain, list_of_atoms)

    return link


def atomBuilder(line):
    atom_type = str(line[:6])
    number = int(line[6:11])
    atom_name = str(line[12:16]).replace(' ', '_')
    alt_loc = str(line[16])
    residue_name = str(line[17:20])
    chain = str(line[21])
    residue_number = int(line[22:26])
    i_code = str(line[26])
    coords = np.array((float(line[30:38]),
                       float(line[38:46]),
                       float(line[46:54])))

    occupancy = line[54:60]
    if (occupancy != '      '):
        occupancy = float(occupancy)

    tempFactor = line[60:66]
    if (tempFactor != '      '):
        tempFactor = float(tempFactor)

    element = str(line[76:78])
    charge = str(line[78:80])

    atom = Atom(atom_type, number, atom_name, alt_loc, residue_name, chain,
                residue_number, i_code, coords, occupancy, tempFactor, element,
                charge)

    return atom


def modelBuilder(list_of_chains, model_number):
    return Model(list_of_chains, model_number)
