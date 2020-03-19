
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
                        help="Relative path to topology")

    args = parser.parse_args()

    return args.cfs_path, args.ligand_resname, args.distance, args.angle, \
        args.pseudo_hb, args.processors_number, args.topology_path


def find_hbonds_in_trajectory(lig_resname, distance, angle, pseudo, traj):
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


def parallel_loop(lig_resname, distance, angle, pseudo_hb,
                  proc_number, topology_path, cf_path):
    # Avoid doing extra work
    cf_path = Path(cf_path)
    print('- Found control file: {}'.format(cf_path))
    if (cf_path.parent.joinpath('hbonds.out').is_file()):
        print('  - Skipping because \'hbonds.out\' already exists')
        return

    print('  - Parsing trajectories...')
    builder = cfp.ControlFileBuilder(cf_path)
    cf = builder.build()
    sim = cf.getSimulation()
    sim.set_topology_path(
        cf_path.parent.joinpath(topology_path))
    sim.getOutputFiles()

    print('  - Detecting hydrogen bonds...')
    hbonds_dict = {}
    for epoch in sim:
        for report in epoch:
            hbonds_dict[(epoch, report.trajectory.name)] = \
                find_hbonds_in_trajectory(lig_resname, distance, angle,
                                          pseudo_hb, report.trajectory.data)

    with open(cf_path.parent.joinpath('hbonds.out'), 'w') as file:
        file.write(str(cf_path.parent.parent) + '\n')
        for (epoch, traj_name), hbonds in hbonds_dict.items():
            for model, hbs in hbonds.items():
                file.write('{}    {:^15}    {:3d}    '.format(
                    epoch.index, traj_name, model))

                for hb in hbs[:-1]:
                    file.write('{},'.format(hb))

                file.write('{}'.format(hbs[-1]))

                file.write('\n')


def main():
    # Parse args
    cfs_path, lig_resname, distance, angle, pseudo_hb, proc_number, \
        topology_path = parse_args()
    cfs_path = glob.glob(cfs_path)

    _parallel_loop = partial(parallel_loop, lig_resname, distance, angle,
                             pseudo_hb, proc_number, topology_path)

    with Pool(proc_number) as pool:
        pool.map(_parallel_loop, cfs_path)


if __name__ == "__main__":
    main()
