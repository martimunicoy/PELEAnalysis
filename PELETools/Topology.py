# -*- coding: utf-8 -*-


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Class definitions
class Topology:
    def __init__(self, template, link):
        self._template = template
        self._link = link

        # Initiate Topology information
        self._initiate()

        # Generate Topology
        self._generateTopology()

    @property
    def template(self):
        return self._template

    @property
    def link(self):
        return self._link

    def _initiate(self):
        self._root_atom = None
        self._parents_dict = {}
        self._childs_dict = {}

        for atom in self.link.list_of_atoms:
            self._parents_dict[atom] = []
            self._childs_dict[atom] = []

    def _generateTopology(self):
        template_atoms = self.template.list_of_atoms

        for atom_id, template_atom in template_atoms.items():
            link_atom = self.link.getAtomWithName(template_atom.pdb_atom_name)

            parent_id = int(template_atom.parent_id)
            if (parent_id == 0):
                self._root_atom = link_atom
            else:
                template_parent = template_atoms[parent_id]
                link_parent = self.link.getAtomWithName(
                    template_parent.pdb_atom_name)

                self._addParent(link_atom, link_parent)
                self._addChild(link_parent, link_atom)

    def _addParent(self, atom, parent):
        self._parents_dict[atom] += [parent, ]

    def _addChild(self, atom, child):
        self._childs_dict[atom] += [child, ]

    def getChildsOfAtom(self, atom):
        return self._childs_dict[atom]

    def getParentsOfAtom(self, atom):
        return self._parents_dict[atom]

    def getRootAtom(self):
        return self._root_atom


# Builder definitions
def buildTopologyFromLinkTemplate(template, link):
    return Topology(template, link)
