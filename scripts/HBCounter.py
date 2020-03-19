
# -*- coding: utf-8 -*-


# Standard imports
import glob
from pathlib import Path
from multiprocessing import Pool

# External imports
import numpy as np
import pandas as pd

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
NUMBER_OF_PROCESSORS = 4


def find_hbonds_in_trajectory(traj):
    # Access to mdtraj's trajectory object
    traj = traj.data
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


def fill_report_row(df_to_fill, traj_file, epoch, snap, hbond):
    df = pd.DataFrame({"trajectory_file": traj_file, "epoch": epoch,
                       "snapshot": snap, "hbond": hbond})
    df_to_fill.append(df)


def main():
    # Parse args
    #args = parse_args()
    cfs_path = glob.glob(
        '/home/carles/test/adaptive.conf')
    print(cfs_path)

    for cf_path in cfs_path:
        print('- Found control file: {}'.format(cf_path))
        print('  - Parsing trajectories...')
        cf_path = Path(cf_path)
        builder = cfp.ControlFileBuilder(cf_path)
        cf = builder.build()
        sim = cf.getSimulation()
        sim.set_topology_path(
            cf_path.parent.joinpath('output/topologies/topology_0.pdb'))
        # sim.set_topology_path(
        #     cf_path.parent.joinpath('output/topologies/conntopology_0.pdb'))
        sim.getOutputFiles(NUMBER_OF_PROCESSORS)

        print('  - Detecting hydrogen bonds...')
        hbonds_dict = {}
        report = pd.DataFrame(columns=["trajectory_file", "epoch",
                                         "snapshot", "hbond"])
        for epoch in sim:
            print('    - Epoch {}'.format(epoch.index))
            with Pool(NUMBER_OF_PROCESSORS) as pool:
                results = pool.map(find_hbonds_in_trajectory,
                                   [report.trajectory for report in epoch])

            for i, traj in enumerate([report.trajectory for report in epoch]):
                hbonds_dict[(epoch, traj.name)] = results[i]

        for key, hbonds in items.hbonds_dict:
            epoch, traj = key
            for model, hbond in items.hbonds:
                fill_report_row(report, traj_file=traj, epoch=epoch,
                                snap=model, hbond=hbond)
        print(report)


if __name__ == "__main__":
    main()
