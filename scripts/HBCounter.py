
# -*- coding: utf-8 -*-


# Standard imports
import glob
from pathlib import Path

# External imports
import numpy as np

# PELE imports
from PELETools import ControlFileParser as cfp
from PELETools.External import hbond_mod as hbm

# Script information
__author__ = "Marti Municoy, Carles Perez"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy, Carles Perez"
__email__ = "marti.municoy@bsc.es, carles.perez@bsc.es"


LIGAND_RESNAME = 'LIG'
DISTANCE = 0.25
ANGLE = 2.0 * np.pi / 3.0
PSEUDO_HB = False


def find_hbonds_in_trajectory(traj):
    lig = traj.topology.select('resname {}'.format(LIGAND_RESNAME))
    hbonds_in_traj = find_ligand_hbonds(traj, lig)

    return hbonds_in_traj


def find_ligand_hbonds(traj, lig):
    #hbonds_lig = {}
    hbonds_dict = {}
    for model_id, snapshot in enumerate(traj):
        results = find_hbond_in_snapshot(snapshot, lig)
        print([(traj.topology.atom(i[0]), traj.topology.atom(i[1]), traj.topology.atom(i[2])) for i in results])
        hbonds_dict[model_id] = results

    return hbonds_dict


def find_hbond_in_snapshot(snapshot, lig):
    hbonds = hbm.baker_hubbard(traj=snapshot, distance=DISTANCE, angle=ANGLE,
                               pseudo=PSEUDO_HB)

    results = []
    for hbond in hbonds:
        if (any(atom in lig for atom in hbond) and not
                all(atom in hbond for atom in lig)):
            results.append(hbond)

    return results


def main():
    # Parse args
    #args = parse_args()
    cfs_path = glob.glob(
        '/Volumes/MacintoshExternal2/COVID/*/adaptive.conf')

    for cf_path in cfs_path:
        cf_path = Path(cf_path)
        builder = cfp.ControlFileBuilder(
            '/Volumes/MacintoshExternal2/COVID/6LU7_MOL0300_bis/adaptive.conf')
        cf = builder.build()
        sim = cf.getSimulation()
        sim.set_topology_path(
            cf_path.parent.joinpath('output/topologies/topology_0.pdb'))
        # sim.set_topology_path(
        #     cf_path.parent.joinpath('output/topologies/conntopology_0.pdb'))
        sim.getOutputFiles()

        hbonds_dict = {}
        for epoch in sim:
            for report in epoch:
                trajectory = report.trajectory
                hbonds_dict[(epoch.index, trajectory.name)] = \
                    find_hbonds_in_trajectory(trajectory.data)


if __name__ == "__main__":
    main()
