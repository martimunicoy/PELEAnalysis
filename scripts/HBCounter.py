
# -*- coding: utf-8 -*-


# Standard imports
import argparse as ap
import glob
from pathlib import Path
from multiprocessing import Pool
from functools import partial

# PELE imports
from PELETools import ControlFileParser as cfp
from PELETools.External import hbond_mod as hbm

# Script information
__author__ = "Marti Municoy, Carles Perez"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy, Carles Perez"
__email__ = "marti.municoy@bsc.es, carles.perez@bsc.es"


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("cfs_path", metavar="PATH", type=str,
                        nargs='*',
                        help="Path to PELE control files")
    parser.add_argument("-l", "--ligand_resname",
                        metavar="LIG", type=str, default='LIG',
                        help="Ligand residue name")
    parser.add_argument("-d", "--distance",
                        metavar="D", type=float, default='0.25',
                        help="Hydrogen bonds distance")
    parser.add_argument("-a", "--angle",
                        metavar="A", type=float, default='2.0943951023931953',
                        help="Hydrogen bonds angle")
    parser.add_argument("-p", "--pseudo_hb",
                        metavar="BOOL", type=bool, default=False,
                        help="Look for pseudo hydrogen bonds")
    parser.add_argument("-n", "--processors_number",
                        metavar="N", type=int, default=None,
                        help="Number of processors")
    parser.add_argument("-t", "--topology_path",
                        metavar="PATH", type=str,
                        default='output/topologies/topology_0.pdb',
                        help="Relativo path to topology")

    args = parser.parse_args()

    return args.cfs_path, args.ligand_resname, args.distance, args.angle, \
        args.pseudo_hb, args.processors_number, args.topology_path


def find_hbonds_in_trajectory(lig_resname, distance, angle, pseudo, traj):
    # Access to mdtraj's trajectory object
    traj = traj.data
    lig = traj.topology.select('resname {}'.format(lig_resname))
    hbonds_in_traj = find_ligand_hbonds(traj, lig, distance, angle, pseudo)

    return hbonds_in_traj


def find_ligand_hbonds(traj, lig, distance, angle, pseudo):
    hbonds_dict = {}
    for model_id, snapshot in enumerate(traj):
        results = find_hbond_in_snapshot(snapshot, lig, distance, angle,
                                         pseudo)
        hbonds_dict[model_id] = results

    return hbonds_dict


def find_hbond_in_snapshot(snapshot, lig, distance, angle, pseudo):
    hbonds = hbm.baker_hubbard(traj=snapshot, distance=distance, angle=angle,
                               pseudo=pseudo)

    results = []
    for hbond in hbonds:
        if (any(atom in lig for atom in hbond) and not
                all(atom in hbond for atom in lig)):
            for atom in hbond:
                if (atom not in lig):
                    results.append(snapshot.topology.atom(atom))
                    break

    return results


def main():
    # Parse args
    cfs_path, lig_resname, distance, angle, pseudo_hb, proc_number, \
        topology_path = parse_args()

    cfs_path_list = []
    if (type(cfs_path) == list):
        for cf_path in cfs_path:
            cfs_path_list += glob.glob(cf_path)

    for cf_path in cfs_path_list:
        print('- Found control file: {}'.format(cf_path))
        print('  - Parsing trajectories...')
        cf_path = Path(cf_path)
        builder = cfp.ControlFileBuilder(cf_path)
        cf = builder.build()
        sim = cf.getSimulation()
        sim.set_topology_path(
            cf_path.parent.joinpath(topology_path))
        sim.getOutputFiles()

        print('  - Detecting hydrogen bonds...')
        hbonds_dict = {}
        parallel_function = partial(find_hbonds_in_trajectory,
                                    lig_resname, distance, angle, pseudo_hb)
        for epoch in sim:
            with Pool(proc_number) as pool:
                results = pool.map(parallel_function,
                                   [report.trajectory for report in epoch])

            for i, traj in enumerate([report.trajectory for report in epoch]):
                hbonds_dict[(epoch, traj.name)] = results[i]

        with open(cf_path.parent.joinpath('hbonds.out'), 'w') as file:
            for (epoch, traj_name), hbonds in hbonds_dict.items():
                for model, hbs in hbonds.items():
                    file.write('{}    {:^15}    {:3d}    '.format(
                        epoch.index, traj_name, model))

                    for hb in hbs:
                        file.write('{},'.format(hb))

                    file.write('\n')


if __name__ == "__main__":
    main()
