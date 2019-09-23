import numpy as np


class Metric(object):
    def __init__(self):
        self._metric_name = "CustomMetric"

    @property
    def metric_name(self):
        return self._metric_name

    def add_to_report(self, report):
        values = self.get_values_from_trajectory(report.trajectory)
        report.addMetric(self.metric_name, values)

    def get_values_from_trajectory(self, trajectory):
        return self._calculate(trajectory)


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
        atoms2 = trajectory.getAtoms(self.atom_name2)

        for atom1, atom2 in zip(atoms1, atoms2):
            values.append(self.__getDistanceBetweenAtoms(atom1, atom2))

        return values

    def __getDistanceBetweenAtoms(self, atom1, atom2):
        vector_from_1_to_2 = np.array(atom2.coords) - \
            np.array(atom1.coords)

        return np.linalg.norm(vector_from_1_to_2)
