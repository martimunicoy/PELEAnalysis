# -*- coding: utf-8 -*-


# Python imports
import sys


# FEP_PELE imports
from .Molecules import atomBuilder, linkBuilder, chainBuilder, modelBuilder
from .Topology import buildTopologyFromLinkTemplate
from .Utils import checkFile, normalize, norm


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Classes
class PDBParser:
    def __init__(self, pdb_path):
        try:
            checkFile(pdb_path)
        except NameError:
            raise NameError("PDBParser Error: no PDB file found in path " +
                            "{}".format(pdb_path))
        self._path = pdb_path

        self._atoms = []
        self._links = []
        self._chains = []
        self._models = []

        self.__temporary_atoms_chunk = []
        self.__temporary_links_chunk = []
        self.__temporary_chains_chunk = []

        self.__current_model = None

        self._processPDB()

    @property
    def path(self):
        return self._path

    @property
    def atoms(self):
        return self._atoms

    @property
    def links(self):
        return self._links

    @property
    def chains(self):
        return self._chains

    @property
    def models(self):
        return self._models

    def getLinkWithId(self, id):
        chain_name, link_number = id.split(':')

        for chain in self.chains:
            if (chain.name == chain_name):
                for link in chain.list_of_links:
                    if (link.number == int(link_number)):
                        return link

    def _processPDB(self):
        with open(self._path, 'r') as file:
            for line in file:
                if (self._foundENDMDL(line)):
                    self._processENDMDL(line)
                    continue

                if (self._foundTER(line)):
                    self._processTER()
                    continue

                if (len(line) <= 6):
                    continue

                line_type = line[0:6]

                if (line_type == "ATOM  "):
                    self._processATOM(line)
                elif (line_type == "HETATM"):
                    self._processHETATM(line)
                elif (line_type == "CONECT"):
                    self._processCONECT(line)
                elif (line_type == "SEQRES"):
                    self._processSEQRES(line)
                elif (line_type == "MODEL "):
                    self._processMODEL(line)
                elif (line_type == "ENDMDL"):
                    self._processENDMDL(line)
                elif (line_type == "REMARK"):
                    self._processREMARK(line)
                else:
                    print("PDBParser Warning: unknown line type " +
                          "{}".format(line))

            # In case a final TER is missing
            if (len(self.__temporary_atoms_chunk) != 0):
                self._processTER()

    def _foundENDMDL(self, line):
        if (len(line) < 6):
            return False

        line_type = line[0:6]

        return line_type == "ENDMDL"

    def _foundTER(self, line):
        if (len(line) < 3):
            return False

        line_type = line[0:3]

        return line_type == "TER" or line_type == "END"

    def _processTER(self):
        # Create last link
        if (len(self.__temporary_atoms_chunk) == 0):
            print("PDBParser Warning: invalid TER location was found")
            return
        self._links.append(linkBuilder(self.__temporary_atoms_chunk))
        self.__temporary_atoms_chunk = []

        # Create last chain
        self.__temporary_links_chunk.append(self.links[-1])
        self._chains.append(chainBuilder(self.__temporary_links_chunk))
        self.__temporary_links_chunk = []

        # Add last chain to temporary chunk
        self.__temporary_chains_chunk.append(self.chains[-1])

    def _processATOM(self, line):
        try:
            checkPDBLine(line)
        except NameError as e:
            raise NameError("PDBParser Error: invalid PBD_line, " +
                            str(e) + ': ' + str(line))

        self._atoms.append(atomBuilder(line))

        self._processLink()

    def _processLink(self):
        if (len(self.__temporary_atoms_chunk) == 0):
            self.__temporary_atoms_chunk.append(self.atoms[-1])
            return

        atom1 = self.atoms[-1]
        atom2 = self.__temporary_atoms_chunk[-1]

        if ((atom1.chain != atom2.chain) or
                (atom1.residue_name != atom2.residue_name) or
                (atom1.residue_number != atom2.residue_number)):
            self._links.append(linkBuilder(self.__temporary_atoms_chunk))
            self.__temporary_atoms_chunk = [atom1, ]
            self._processChain()
        else:
            self.__temporary_atoms_chunk.append(atom1)

    def _processChain(self):
        if (len(self.__temporary_links_chunk) == 0):
            self.__temporary_links_chunk.append(self.links[-1])
            return

        link1 = self.links[-1]
        link2 = self.__temporary_links_chunk[-1]

        if (link1.chain != link2.chain):
            self._chains.append(chainBuilder(self._temporary_links_chunk))
            self.__temporary_chains_chunk.append(self.chains[-1])
            self.__temporary_links_chunk = [link1, ]
        else:
            self.__temporary_links_chunk.append(link1)

    def _processHETATM(self, line):
        self._processATOM(line)
        self._atoms[-1].setAsHeteroatom()

    def _processCONECT(self, line):
        pass

    def _processSEQRES(self, line):
        pass

    def _processMODEL(self, line):
        try:
            self.__current_model = int(line[6:])
        except (IndexError, NameError):
            raise NameError("PDBParser Error: invalid PBD_line: " +
                            str(line))

    def _processENDMDL(self, line):
        if (self.__current_model is None):
            raise IOError("PDBParser Error: found ENDMDL line before MODEL " +
                          "line" + str(line))

        # In case the final chain of the model has not been closed
        # (ENDMDL without TER)
        if (len(self.__temporary_atoms_chunk) != 0):
            self._processTER()

        # Create Model
        self._models.append(modelBuilder(self.__temporary_chains_chunk,
                                         self.__current_model))

        self.__temporary_chains_chunk = []
        self.__current_model = None

    def _processREMARK(self, line):
        pass


def checkPDBLine(PDB_line):
    okay = True
    messages = []

    # Check type
    if (type(PDB_line) != str):
        okay = False
        messages.append("invalid type")

    # Check length
    if (len(PDB_line) < 77):
        okay = False
        messages.append("invalid length")

    if (not okay):
        raise NameError(', '.join(messages))


def getLineType(PDB_line):
    try:
        checkPDBLine(PDB_line)
    except NameError as e:
        raise NameError("PDBTools.getLineType Error: invalid PBD_line, " +
                        str(e))

    return PDB_line[0:6]


def getAtomName(PDB_line):
    try:
        checkPDBLine(PDB_line)
    except NameError as e:
        raise NameError("PDBTools.getAtomName Error: invalid PBD_line, " +
                        str(e))

    return PDB_line[12:16]


class PDBModifier(object):
    def __init__(self, pdb):
        self._pdb = pdb

        # In case a link has to be modified
        self._link = None
        self._link_template = None

        # General Topology attribute
        self._topology = None

    @property
    def pdb(self):
        return self._pdb

    @property
    def link(self):
        return self._link

    @property
    def link_template(self):
        return self._link_template

    @property
    def topology(self):
        return self._topology

    def setLinkToModify(self, link, link_template):
        if (link.name != link_template.template_name):
            raise NameError("Link and Template do not match")

        self._link = link
        self._link_template = link_template
        self._topology = buildTopologyFromLinkTemplate(link_template, link)

    def modifyBond(self, bond_to_modify, new_length, fixed_atom=0):
        first_atom_to_modify = self.link.getAtomWithName(
            bond_to_modify[bool(fixed_atom == 0)])

        fixed_atom = self.link.getAtomWithName(
            bond_to_modify[fixed_atom])

        excluded_atoms = [fixed_atom, ]

        vector = normalize(fixed_atom.coords - first_atom_to_modify.coords)[0]
        length = norm(fixed_atom.coords - first_atom_to_modify.coords) - \
            new_length

        self._recursiveBondModifier(first_atom_to_modify, excluded_atoms,
                                    vector, length)

    def _recursiveBondModifier(self, atom, excluded_atoms, vector, length):
        excluded_atoms.append(atom)

        atom.setNewCoords(atom.coords + vector * length)

        connected_atoms = []

        for child in self.topology.getChildsOfAtom(atom):
            if (child not in excluded_atoms):
                connected_atoms.append(child)

        for parent in self.topology.getParentsOfAtom(atom):
            if (parent not in excluded_atoms):
                connected_atoms.append(parent)

        for connected_atom in connected_atoms:
            self._recursiveBondModifier(connected_atom, excluded_atoms, vector,
                                        length)

    def write(self, output_path):
        writer = PDBWriter(self.pdb)
        writer.write(output_path)


class PDBWriter(object):
    def __init__(self, pdb_object):
        self._pdb = pdb_object

    def write(self, output_path):
        with open(output_path, 'w') as f:
            chains = sorted(self._pdb.chains)

            for chain in chains:
                links = sorted(chain.list_of_links)

                for link in links:
                    atoms = sorted(link.list_of_atoms)

                    for atom in atoms:
                        f.write(self._getAtomLine(atom))
                f.write(self._getTERLine())

    def _getAtomLine(self, atom):
        return "{}".format(atom.atom_type) + \
            "{:5d}".format(atom.number) + ' ' + \
            "{}".format(atom.atom_name.replace('_', ' ')) + \
            "{}".format(atom.alt_loc) + \
            "{}".format(atom.residue_name) + ' ' + \
            "{}".format(atom.chain) + \
            "{:4d}".format(atom.residue_number) + \
            "{}".format(atom.i_code) + '   ' + \
            "{: 8.3f}".format(atom.coords[0]) + \
            "{: 8.3f}".format(atom.coords[1]) + \
            "{: 8.3f}".format(atom.coords[2]) + \
            "{: 6.2f}".format(atom.occupancy) + \
            "{: 6.2f}".format(atom.tempFactor) + \
            '          ' + \
            "{}".format(atom.element) + \
            "{}".format(atom.charge) + '\n'

    def _getTERLine(self):
        return "TER\n"


class PDBHandler:
    def __init__(self, simulation):
        self.simulation = simulation
        self.trajectory = None
        self.are_atoms_indexed = False
        self.indexedAtoms = None
        self.system_size = None

    def getSystemSize(self):
        if (self.system_size is not None):
            return self.system_size

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

    def currentModel(self, line):
        return int(line / (self.system_size + 1))
