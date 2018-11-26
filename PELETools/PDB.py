# -*- coding: utf-8 -*-


# Imports
import sys


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Classes
class PDBHandler:
    def __init__(self, simulation):
        self.simulation = simulation
        self.trajectory = None
        self.are_atoms_indexed = False
        self.indexedAtoms = None
        self.system_size = None

    def getSystemSize(self):
        if (self.trajectory is None):
            self.trajectory = self.simulation[0].trajectory

        path = self.trajectory.path + '/' + self.trajectory.name

        with open(path) as trajectory_file:
            for size, line in enumerate(trajectory_file):
                if line.startswith("ENDMDL"):
                    break

        return size + 1

    def indexAtoms(self):
        self.indexedAtoms = {}

        if (self.trajectory is None):
            self.trajectory = self.simulation[0].trajectory

        if self.system_size is None:
            self.system_size = self.getSystemSize()

        path = self.trajectory.path + '/' + self.trajectory.name

        with open(path) as trajectory_file:
            for i, line in enumerate(trajectory_file):
                if len(line) < 80:
                    continue
                if (int(i / (self.system_size + 1)) > 0):
                    break

                linetype = line.split()[0]
                chain = line[21]
                number = int(line[23:26])
                name = line[12:16]

                if linetype in ["HETATM", "ATOM"]:
                    if chain in self.indexedAtoms:
                        if number in self.indexedAtoms[chain]:
                            if type(self.indexedAtoms[chain][number]) != dict:
                                self.indexedAtoms[chain][number] = {}
                            self.indexedAtoms[chain][number][name] = i
                        else:
                            if type(self.indexedAtoms[chain]) != dict:
                                self.indexedAtoms[chain] = {}
                            self.indexedAtoms[chain][number] = {}
                            self.indexedAtoms[chain][number][name] = {}
                    else:
                        self.indexedAtoms[chain] = {}
                        self.indexedAtoms[chain][number] = {}
                        self.indexedAtoms[chain][number][name] = {}

                    self.indexedAtoms[chain][number][name] = i

        self.are_atoms_indexed = True

    def getAtomLineInPDB(self, atom_data):
        if (not self.are_atoms_indexed):
            print("PDBHandler:getAtomLineInPDB: Error, PDB atoms are not " +
                  "indexed")
            sys.exit(1)

        chain, number, name = atom_data
        number = int(number)

        try:
            line_number = self.indexedAtoms[chain][number][name]
        except KeyError:
            print("PDBHandler:getAtomLineInPDB: Error, atom " +
                  "{} not found in PDBHandler indexed ".format(atom_data) +
                  "information")
            sys.exit(1)
        return line_number

    def getLinkLinesInPDB(self, link_data):
        if (not self.are_atoms_indexed):
            print("PDBHandler:getAtomLineInPDB: Error, PDB atoms are not " +
                  "indexed")
            sys.exit(1)

        chain, number = link_data
        number = int(number)

        try:
            link_lines = self.indexedAtoms[chain][number]
        except KeyError:
            print("PDBHandler:getLinkLinesInPDB: Error, link " +
                  "{} not found in PDBHandler indexed ".format(link_data) +
                  "information")
            sys.exit(1)
        return link_lines
