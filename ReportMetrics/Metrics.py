import numpy as np

from PELETools.PDB import PDBParser


class Metric(object):
    def __init__(self):
        self._metric_name = "CustomMetric"
        self._try_to_append = False

    @property
    def metric_name(self):
        return self._metric_name

    @property
    def try_to_append(self):
        return self._try_to_append

    def add_to_report(self, report):
        values = self.get_values_from_trajectory(report.trajectory)
        report.addMetric(self.metric_name, values, self.try_to_append)

    def get_values_from_trajectory(self, trajectory):
        return self._calculate(trajectory)

    def set_report_appending_behaviour(self, value):
        self._try_to_append = value


class AtomsInsideSphere(Metric):
    def __init__(self, atom_names, center, radius, metric_name="InsideSphere"):
        Metric.__init__(self)
        self._atom_names = atom_names
        self._center = center
        self._radius = radius
        self._metric_name = metric_name

    @property
    def atom_names(self):
        return self._atom_names

    @property
    def center(self):
        return self._center

    @property
    def radius(self):
        return self._radius

    def _calculate(self, trajectory):
        values_per_atom_name = []
        for atom_name in self.atom_names:
            atom_inside_sphere_metric = AtomInsideSphere(atom_name,
                                                         self.center,
                                                         self.radius)
            atom_inside_sphere_metric.calculate()
            values_per_atom_name.append(atom_inside_sphere_metric.values)

        return [any(i) for i in zip(*values_per_atom_name)]


class AtomInsideSphere(Metric):
    def __init__(self, atom_name, center, radius, metric_name="InsideSphere"):
        Metric.__init__(self)
        self._atom_name = atom_name
        self._center = np.array(center)
        self._radius = radius
        self._squared_radius = pow(radius, 2)
        self._metric_name = metric_name

    @property
    def atom_name(self):
        return self._atom_name

    @property
    def center(self):
        return self._center

    @property
    def radius(self):
        return self._radius

    @property
    def squared_radius(self):
        return self._squared_radius

    def _calculate(self, trajectory):
        values = []
        atoms = trajectory.getAtoms(self.atom_name)

        for atom in atoms:
            values.append(self.__isAtomInsideSphere(atom))

    def __isAtomInsideSphere(self, atom):
        diff = np.array(self.center) - np.array(atom.coords)

        return np.dot(diff, diff) < self.squared_radius


class DistanceBetweenAtoms(Metric):
    def __init__(self, atom_name1, atom_name2,
                 metric_name="DistanceBetweenAtoms"):
        Metric.__init__(self)
        self._atom_name1 = atom_name1
        self._atom_name2 = atom_name2
        self._metric_name = metric_name

    @property
    def atom_name1(self):
        return self._atom_name1

    @property
    def atom_name2(self):
        return self._atom_name2

    def _calculate(self, trajectory):
        values = []

        atoms1 = trajectory.getAtoms(self.atom_name1)
        if (len(atoms1) == 0):
            raise NameError('Atom {} '.format(self.atom_name1) +
                            'not found in {}/{}'.format(trajectory.path,
                                                        trajectory.name))

        atoms2 = trajectory.getAtoms(self.atom_name2)
        if (len(atoms2) == 0):
            raise NameError('Atom {} '.format(self.atom_name1) +
                            'not found in {}/{}'.format(trajectory.path,
                                                        trajectory.name))

        for atom1, atom2 in zip(atoms1, atoms2):
            values.append(self.__getDistanceBetweenAtoms(atom1, atom2))

        return values

    def __getDistanceBetweenAtoms(self, atom1, atom2):
        vector_from_1_to_2 = np.array(atom2.coords) - \
            np.array(atom1.coords)

        return np.linalg.norm(vector_from_1_to_2)


class LinkRMSD(Metric):
    def __init__(self, reference_pdb, link_selection, atom_pairs=None,
                 metric_name="RMSD"):
        Metric.__init__(self)
        self._reference_pdb = PDBParser(reference_pdb)
        self._link_selection = link_selection
        self._atom_pairs = atom_pairs
        self._metric_name = metric_name

        # Get list of reference atoms
        self._reference_atoms = []
        reference_link = self.reference_pdb.getLinkWithId(link_selection)
        if (reference_link is None):
            raise NameError('Selected link \'{}\' '.format(link_selection) +
                            'not found in reference pdb')
        for atom in reference_link:
            self._reference_atoms.append(atom)

        # Actions to perform only if atom pairs are defined
        if (atom_pairs is not None):
            # Check that all atom pairs are in reference_atoms
            for atom_pair in atom_pairs:
                reference_name, _ = atom_pair
                if (reference_name not in [atom.atom_name for atom in
                                           self._reference_atoms]):
                    raise NameError('Reference atom name ' +
                                    '{} '.format(reference_name) +
                                    'not found in reference trajectory link ' +
                                    '{}'.format(self.link_selection))

            # Filter reference atoms
            for atom in self._reference_atoms:
                if (atom.atom_name not in [atom_pair[0] for atom_pair
                                           in self.atom_pairs]):
                    self._reference_atoms.remove(atom)

        # Make pairs between atom names and atom objects
        self._reference_pairs = {}
        for atom in self._reference_atoms:
            self._reference_pairs[atom.atom_name] = atom

    @property
    def reference_pdb(self):
        return self._reference_pdb

    @property
    def link_selection(self):
        return self._link_selection

    @property
    def atom_pairs(self):
        return self._atom_pairs

    def _calculate(self, trajectory):

        if (self.atom_pairs is not None):
            return self._calculate_using_atom_pairs(trajectory)
        else:
            return self._calculate_without_atom_pairs(trajectory)

    def _calculate_using_atom_pairs(self, trajectory):
        values = []

        # Get list of simulation atoms
        chain_name, link_number = self.link_selection.split(':')
        reference_links = trajectory.getLinks((chain_name, int(link_number)))

        for link in reference_links:
            simulation_atoms = []
            for atom in link:
                simulation_atoms.append(atom)

            # Check that all atom pairs are in simulation atoms and
            # create simulation pairs
            simulation_pairs = {}
            for atom_pair in self.atom_pairs:
                _, simulation_name = atom_pair
                for atom in simulation_atoms:
                    if (simulation_name == atom.atom_name):
                        simulation_pairs[simulation_name] = atom
                        break
                else:
                    raise NameError('Reference atom name ' +
                                    '{} '.format(simulation_name) +
                                    'not found in simulation trajectory ' +
                                    'link {}'.format(self.link_selection))

            sum_of_squared_distances = 0

            for (reference_name, simulation_name) in self.atom_pairs:
                reference_atom = self._reference_pairs[reference_name]
                simulation_atom = simulation_pairs[simulation_name]
                sum_of_squared_distances += \
                    self.__getSquaredDistanceBetweenAtoms(reference_atom,
                                                          simulation_atom)

            values.append(np.sqrt(sum_of_squared_distances /
                                  len(self.atom_pairs)))

        return values

    def _calculate_without_atom_pairs(self, trajectory):
        values = []

        # Get list of simulation atoms
        chain_name, link_number = self.link_selection.split(':')
        reference_links = trajectory.getLinks((chain_name, int(link_number)))

        for link in reference_links:
            simulation_atoms = []
            for atom in link:
                simulation_atoms.append(atom)

            # Check that all atom pairs are in simulation atoms and
            # create simulation pairs
            simulation_pairs = {}
            for atom in simulation_atoms:
                simulation_pairs[atom.atom_name] = atom

            sum_of_squared_distances = 0

            for reference_name, reference_atom in \
                    self._reference_pairs.items():
                if (reference_name not in simulation_pairs.keys()):
                    raise NameError('Reference name ' +
                                    '\'{}\' '.format(reference_name) +
                                    'not found in trajectory pdb')

                reference_atom = self._reference_pairs[reference_name]
                simulation_atom = simulation_pairs[reference_name]
                sum_of_squared_distances += \
                    self.__getSquaredDistanceBetweenAtoms(reference_atom,
                                                          simulation_atom)

            values.append(np.sqrt(sum_of_squared_distances /
                                  len(self._reference_pairs.keys())))

        return values

    def __getSquaredDistanceBetweenAtoms(self, atom1, atom2):
        vector_from_1_to_2 = np.array(atom2.coords) - \
            np.array(atom1.coords)

        return (vector_from_1_to_2**2).sum()


class DoubleBondSide(Metric):
    def __init__(self, double_bond_atom1, double_bond_atom2, plane_atom_name3,
                 outer_atom_name4, metric_name="DoubleBondSide"):
        Metric.__init__(self)
        self._double_bond_atom1 = double_bond_atom1
        self._double_bond_atom2 = double_bond_atom2
        self._plane_atom_name3 = plane_atom_name3
        self._outer_atom_name4 = outer_atom_name4
        self._metric_name = metric_name

    @property
    def double_bond_atom1(self):
        return self._double_bond_atom1

    @property
    def double_bond_atom2(self):
        return self._double_bond_atom2

    @property
    def plane_atom_name3(self):
        return self._plane_atom_name3

    @property
    def outer_atom_name4(self):
        return self._outer_atom_name4

    def _calculate(self, trajectory):
        values = []

        atoms1 = trajectory.getAtoms(self.double_bond_atom1)
        if (len(atoms1) == 0):
            raise NameError('Atom {} '.format(self.double_bond_atom1)
                            + 'not found in {}/{}'.format(trajectory.path,
                                                          trajectory.name))

        atoms2 = trajectory.getAtoms(self.double_bond_atom2)
        if (len(atoms2) == 0):
            raise NameError('Atom {} '.format(self.double_bond_atom2)
                            + 'not found in {}/{}'.format(trajectory.path,
                                                          trajectory.name))

        atoms3 = trajectory.getAtoms(self.plane_atom_name3)
        if (len(atoms2) == 0):
            raise NameError('Atom {} '.format(self.plane_atom_name3)
                            + 'not found in {}/{}'.format(trajectory.path,
                                                          trajectory.name))

        atoms4 = trajectory.getAtoms(self.outer_atom_name4)
        if (len(atoms2) == 0):
            raise NameError('Atom {} '.format(self.outer_atom_name4)
                            + 'not found in {}/{}'.format(trajectory.path,
                                                          trajectory.name))

        assert len(atoms1) == len(atoms2) and len(atoms1) == len(atoms3) \
            and len(atoms1) == len(atoms4), \
            'We expect to find the same number of atoms for each supplied ' \
            + 'atom name'

        for atom1, atom2, atom3, atom4 in zip(atoms1, atoms2, atoms3, atoms4):
            values.append(self._getPlane(atom1, atom2, atom3, atom4))

        return values

    def _getPlane(self, atom1, atom2, atom3, atom4):
        if (not np.array_equal(atom1.coords, atom2.coords)
                and not np.array_equal(atom1.coords, atom3.coords)
                and not np.array_equal(atom1.coords, atom4.coords)):
            v1 = atom2.coords - atom1.coords
            v2 = atom3.coords - atom1.coords
            v3 = atom4.coords - atom1.coords

            if not np.array_equal(v1, v2):
                plane_norm_v = np.cross(v1, v2)

                u_v3 = v3 / np.linalg.norm(v3)
                u_plane_norm_v = plane_norm_v / np.linalg.norm(plane_norm_v)

                angle = np.arccos(np.dot(u_plane_norm_v, u_v3))

                # If angle between vectors is lower than 60 degrees
                if angle < 1.05:
                    face_sign = 1
                # If angle between vectors is higher than 120 degrees
                elif angle > 2.09:
                    face_sign = -1
                else:
                    face_sign = 0

        return face_sign
