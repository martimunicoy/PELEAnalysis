# -*- coding: utf-8 -*-


# Imports
import os
import argparse as ap
import numpy as np
from multiprocessing import cpu_count, Pool
from functools import partial
from sklearn import cluster
from collections import defaultdict
from copy import copy
from pathlib import Path

from PELETools import ControlFileParser
from PELETools.Utils import Logger


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Constants
WATER_OXYGEN_NAME = '_OW_'


# Functions
def parseArgs():
    """Parse arguments from command-line.

    RETURNS
    -------
    control_file_path : string
                        path to PELE control file.
    number_of_processors: int
                          number of processors that will be used to read the
                          trajectories and clusterize all the points.
    water_ids: list of strings
               each string defines a water link that will be tracked and used
               in the clusterization method.
    ref_coords : list of numpy arrays
                 reference coordinates that will be used to calculate the
                 number of water matches.
    cluster_radius : int
                     radius that defines the width of each cluster.
    first_steps_to_ignore : int
                            number of first steps that will be filtered out.
    centroids_output_path : string
                            path for the output PDB file containing the
                            centroids.
    normalize_densities : boolean
                          whether to normalize the density values or not.
    """

    def parse_coords(list_of_coords):
        """ It parses a 3D vector of coordinates

        PARAMETERS
        ----------
        list_of_coords : list of lists
                         list of 3D coordinates to parse from the command-line.

        RETURNS
        -------
        parsed_coords : list of floats
                        list of parsed 3D coordinates.
        """

        parsed_coords = []

        if list_of_coords is not None:
            for coords in list_of_coords:
                parsed_coords.append(np.array(coords))

        return parsed_coords

    def check_output_path(path):
        """ It checks the output path to save resulting centroids

        PARAMETERS
        ----------
        path : string
               path for the output PDB file containing the
               centroids.

        RETURNS
        -------
        path : Path object
               path for the output PDB file containing the
               centroids.
        """
        # Check output path
        path = Path(path)
        if (path.is_dir()):
            path = path.joinpath('centroids.pdb')
        elif (not path.is_file()):
            log = Logger()
            log.warning('write_centroids Warning: invalid path to ' +
                        '\'{}\''.format(path))

        return path

    parser = ap.ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-c", "--control_file", required=True,
                          metavar="FILE", type=str,
                          help="path to PELE control file")
    optional.add_argument("-n", "--number_of_processors", metavar="INT",
                          type=int, help="number of processors " +
                          "that will be used to read the trajectories and " +
                          "clusterize all the points", default=None)
    optional.add_argument("-w", "--water_id",
                          metavar="CHAIN_ID:RESIDUE_NUMBER",
                          action='append', dest='water_ids',
                          type=str, help="selection of one water " +
                          "link to track in the clusterization. More than " +
                          "one water can be selected by adding multiple " +
                          "water id arguments", default=None)
    optional.add_argument("-r", "--reference_coordinates",
                          metavar="CHAIN_ID_RESIDUE_NUMBER",
                          action='append', dest='ref_coords', nargs=3,
                          type=float, help="reference coordinates that will " +
                          "be used to calculate the number of water matches")
    optional.add_argument("-f", "--first_steps_to_ignore", metavar="INT",
                          type=int, help="Number of first steps that will " +
                          "be filtered out", default=1)
    optional.add_argument("-R", "--cluster_radius", metavar="FLOAT",
                          type=float, default=2)
    optional.add_argument("-o", "--centroids_output_path", required=False,
                          metavar="PATH", type=str, default='centroids.pdb',
                          help="output path to save the centroids PDB file")
    optional.add_argument("--normalize_densities", dest='normalize_densities',
                          action='store_true', help="clustering densities " +
                          "are normalized in the output files")

    parser.set_defaults(normalize_densities=False)

    parser._action_groups.append(optional)
    args = parser.parse_args()

    parsed_ref_coords = parse_coords(args.ref_coords)
    centroids_output_path = check_output_path(args.centroids_output_path)

    return args.control_file, args.number_of_processors, args.water_ids, \
        parsed_ref_coords, args.first_steps_to_ignore, args.cluster_radius, \
        centroids_output_path, args.normalize_densities


def parse_water_ids(water_ids):
    def parse_list(water_id):
        if (len(water_id != 2) and len(water_id != 3)):
            raise TypeError('Invalid water id list')
        else:
            chain_id = water_id[0]
            residue_number = water_id[1]
            if (len(water_id == 3)):
                atom_name = water_id[2]
            else:
                atom_name = WATER_OXYGEN_NAME
            return [chain_id, residue_number, atom_name]

    def parse_str(water_id):
        fields = water_id.split(':')
        if (len(fields) != 2 and len(fields) != 3):
            raise TypeError('Invalid format for water id. The valid dormat ' +
                            'is: \'CHAIN_ID:RESIDUE_NUMBER\'')
        else:
            if (len(fields) == 3):
                chain_id, residue_number, atom_name = fields
            else:
                chain_id, residue_number = fields
                atom_name = WATER_OXYGEN_NAME

            return [chain_id, residue_number, atom_name]

    if ((water_ids is None) or
        (type(water_ids) is not list and
         type(water_ids) is not tuple)):
        return None

    parsed_water_ids = []
    for water_id in water_ids:
        if (type(water_id) is list):
            parsed_water_ids.append(parse_list(water_id))
        elif (type(water_id) is tuple):
            parsed_water_ids.append(parse_list(water_id))
        elif (type(water_id) is str):
            parsed_water_ids.append(parse_str(water_id))
        else:
            print("Warning: water id {} has an unknown format".format(
                  water_id))

    if (len(parsed_water_ids) == 0):
        return None

    return parsed_water_ids


def arguments_validation(control_file_path, number_of_processors, water_ids):
    """It checks up some of the arguments that are retrieved from command line.

    PARAMETERS
    ----------
    control_file_path : string
                        path to PELE control file.
    number_of_processors: int
                          number of processors that will be used to read the
                          trajectories and clusterize all the points.
    water_ids : list of water ids
                each water id defines a water link that will be tracked and
                used in the clusterization method.

    RETURNS
    -------
    water_ids : list of lists
                each sublist contains the chain id, the residue number and the
                PDB atom name that defines the main atom of a water link.
    number_of_processors: int
                          number of processors that will be used to read the
                          trajectories and clusterize all the points.
    """
    if (not os.path.isfile(control_file_path)):
        raise NameError("Invalid path to PELE control file. " +
                        "File does not exist.")

    if (water_ids is None):
        """
        TODO add this functionality
        print('Warning: no water ids were supplied. The algorithm will track' +
              'all water links that present found in the pdb.')
        """
        raise NotImplementedError("No water id was supplied. Currently, " +
                                  "the algorithm needs at least one water " +
                                  "molecule to track in the clusterization.")
    else:
        water_ids = parse_water_ids(water_ids)

    if (number_of_processors is None):
        number_of_processors = cpu_count()

    return water_ids, number_of_processors


def _parallel_atom_getter(water_simulation_ids, report):
    """This function needs to be called by multiprocessing.Pool method
    and it will retrieve the data about the selected water molecules.

    PARAMETERS
    ----------
    water_simulation_ids : list of lists
                           each sublist contains the chain id, the residue
                           number and the PDB atom name that defines the
                           main atom of a water link
    report : PELETools.SimulationParser.Report object
             it contains information about a PELE report

    RETURNS
    -------
    atom_data : list
                list that contains information about all water links that
                were retrieved
    """
    atom_coords = {}
    for i, water_id in enumerate(water_simulation_ids):
        n_steps = report.getMetric(2)
        atoms = report.trajectory.getAtoms(water_id)
        for j, (step, atom) in enumerate(zip(n_steps, atoms)):
            atom_coords[(i, j, step)] = atom.coords

    atom_data = ((report.path, report.name), atom_coords)
    return atom_data


def obtain_water_data_from(control_file_path, number_of_processors,
                           water_simulation_ids):
    """It obtains data about the chosen water molecules from PELE simulations.

    PARAMETERS
    ----------
    control_file_path : string
                        path to PELE control file
    number_of_processors: int
                          number of processors that will be used to read the
                          trajectories and clusterize all the points
    water_simulation_ids : list of lists
                           each sublist contains the chain id, the residue
                           number and the PDB atom name that defines the
                           main atom of a water link

    RETURNS
    -------
    fixed_atom_data : list
                      list that contains information about all water links that
                      were retrieved
    list_of_reports : list
                      list of all the reports that were retrieved from the PELE
                      simulation that has been read.
    """
    def split_atom_data(atom_data):
        """It splits atom data.

        PARAMETERS
        ----------
        atom_data : list
                    list that contains information about all water links that
                    were retrieved.

        RETURNS
        -------
        atom_reports : list
                       list of ordered atom reports.
        atom_ids : list
                   list of ordered atom ids.
        atom_models : list
                      list of ordered models.
        atom_steps : list
                     list of ordered atom steps.
        atom_coords : list
                      list of ordered atom coordinates.
        """
        atom_reports = []
        atom_ids = []
        atom_models = []
        atom_steps = []
        atom_coords = []

        for data in atom_data:
            for (water_id, model, step), coords in data[1].items():
                atom_reports.append(data[0])
                atom_ids.append(water_id)
                atom_models.append(model)
                atom_steps.append(step)
                atom_coords.append(coords)

        return atom_reports, atom_ids, atom_models, atom_coords, atom_steps

    log = Logger()
    log.info('   - Parsing control file...')
    builder = ControlFileParser.ControlFileBuilder(control_file_path)
    cf = builder.build()
    sim = cf.getSimulation()
    log.info('   - Listing reports...')
    list_of_reports = []
    for epoch in sim:
        for report in epoch:
            list_of_reports.append(report)

    log.info('   - Retrieving data using {} '.format(number_of_processors) +
          'processors...')
    parallel_function = partial(_parallel_atom_getter, water_simulation_ids)
    with Pool(number_of_processors) as pool:
        atom_data = pool.map(parallel_function, list_of_reports)

    fixed_atom_data = []

    log.info('   - Linking report pointers...')
    for (path, name), atom_coords in atom_data:
        for report in list_of_reports:
            if ((report.path, report.name) == (path, name)):
                report_pointer_to_add = report
                break
        else:
            raise NameError("Report {}{} not found".format(path, name))
        fixed_atom_data.append((report_pointer_to_add, atom_coords))

    log.info('   - Parsing data...')
    return split_atom_data(fixed_atom_data), list_of_reports


def filter_structures(atom_reports, atom_ids, atom_models, atom_coords,
                      atom_steps, first_steps_to_ignore):
    """It filters structures that were previously retrieved from a PELE
    simulation.

    PARAMETERS
    ----------
    atom_reports : list
                   list of ordered atom reports.
    atom_ids : list
               list of ordered atom ids.
    atom_models : list
                  list of ordered models.
    atom_steps : list
                 list of ordered atom steps.
    atom_coords : list
                  list of ordered atom coordinates.
    first_steps_to_ignore : int
                            number of first steps that will be filtered out.

    RETURNS
    -------
    f_atom_reports : list
                     filtered list of ordered atom reports.
    f_atom_ids : list
                 filtered list of ordered atom ids.
    f_atom_models : list
                    filtered list of ordered models.
    f_atom_steps : list
                   filtered list of ordered atom steps.
    f_atom_coords : list
                    filtered list of ordered atom coordinates.
    """
    # Remove coordinates from first steps
    f_atom_reports = []
    f_atom_ids = []
    f_atom_models = []
    f_atom_coords = []
    f_atom_steps = []

    for report, atom, model, coords, step in zip(atom_reports,
                                                 atom_ids,
                                                 atom_models,
                                                 atom_coords,
                                                 atom_steps):
        if (step < first_steps_to_ignore):
            continue

        f_atom_reports.append(report)
        f_atom_ids.append(atom)
        f_atom_models.append(model)
        f_atom_coords.append(coords)
        f_atom_steps.append(step)

    return f_atom_reports, f_atom_ids, f_atom_models, f_atom_coords, \
        f_atom_steps


def clusterization(cluster_radius, number_of_processors, atom_coords):
    """ It builds the clusters according to the atomic coordinates that are
    supplied.

    PARAMETERS
    ----------
    cluster_radius : int
                     radius that defines the width of each cluster.
    number_of_processors: int
                          number of processors that will be used to read the
                          trajectories and clusterize all the points.
    atom_coords : list
                  filtered list of ordered atom coordinates.

    RETURNS
    -------
    estimator : sklearn.cluster.MeanShift object
                clusterization implementation that clusterizes through the
                MeanShift method.
    results : list
              list with the results of the clusterization. Each element is the
              cluster in which each atom belongs.
    """
    if (number_of_processors > 2 and number_of_processors == cpu_count()):
        number_of_processors = int(number_of_processors / 2)

    estimator = cluster.MeanShift(bandwidth=cluster_radius,
                                  n_jobs=number_of_processors,
                                  cluster_all=True)
    results = estimator.fit_predict(atom_coords)

    return estimator, results


def get_density(atom_ids, results, estimator, water_simulation_ids):
    """ It calculates the densities of each cluster. That means the number of
    times a water molecule visited each cluster along the whole simulation.

    PARAMETERS
    ----------
    atom_ids : list
               list of ordered atom ids.
    results : list
              list with the results of the clusterization. Each element is the
              cluster in which each atom belongs.
    estimator : sklearn.cluster.MeanShift object
                clusterization implementation that clusterizes through the
                MeanShift method.
    water_simulation_ids : list of lists
                           each sublist contains the chain id, the residue
                           number and the PDB atom name that defines the
                           main atom of a water link.

    RETURNS
    -------
    density : dictionary
              dictionary with cluster ids as keys and their corresponding
              densities as items.
    """
    n_clusters = len(estimator.cluster_centers_)

    # Initialize density dictionary
    density = {}
    for iteration_id in range(0, n_clusters):
        density[iteration_id] = 0

    for water_id in range(0, len(water_simulation_ids)):
        for i, atom_id in enumerate(atom_ids):
            if (atom_id == water_id):
                density[results[i]] += 1

    # Normalize
    norm_factor = 1 / (len(results))

    for iteration_id in range(0, n_clusters):
        density[iteration_id] *= norm_factor

    return density


def print_density_results(densities, reference_clusters=[]):
    """ It prints the density results.

    PARAMETERS
    ----------
    densities : dictionary
                dictionary with cluster ids as keys and their corresponding
                densities as items.
    reference_clusters : list
                         list of clusters that belong to the reference.
    """
    log = Logger()

    log.info('     Ref', 'Cluster n.', 'Probability')
    for cluster_n, cluster_density in densities.items():
        if cluster_density < 0.01:
            continue
        if (cluster_n in reference_clusters):
            log.info('      *    ' +
                     '{:3d}        {:5.3f}'.format(int(cluster_n),
                                                   float(cluster_density)))
        else:
            log.info('           ' +
                     '{:3d}        {:5.3f}'.format(int(cluster_n),
                                                   float(cluster_density)))


def write_centroids(estimator, densities, centroids_output_path,
                    normalize):
    """ It writes the centroids as a PDB file.

    PARAMETERS
    ----------
    estimator : sklearn.cluster.MeanShift object
                clusterization implementation that clusterizes through the
                MeanShift method.
    densities : dictionary
                dictionary with cluster ids as keys and their corresponding
                densities as items.
    centroids_output_path : string
                            path for the output PDB file containing the
                            centroids.
    normalize : boolean
                whether to normalize the density values or not.
    """
    # Writer functions
    def single_write(f, i, centroid, density=None):
        f.write("ATOM    {:3d}  CEN BOX A {:3d} {:>11.3f}{:>8.3f}{:>8.3f}  1.00  0.00\n".format(i, i, *centroid))

    def density_write(f, i, centroid, density):
        f.write("ATOM    {:3d}  CEN BOX A {:3d} {:>11.3f}{:>8.3f}{:>8.3f}  1.00{:>5.2f}\n".format(i, i, *centroid, density))

    # Get centroids and number of clusters
    centroids = estimator.cluster_centers_
    n_clusters = len(centroids)

    # Select writer function
    writer = single_write
    if (densities is not None):
        if (len(densities) == len(centroids)):
            writer = density_write

    # Normalize
    norm_densities = densities
    if (normalize):
        if (densities):
            normalization_factor = 1 / max(densities.values())
            norm_densities = []
            for density in densities.values():
                norm_densities.append(density * normalization_factor)

    # Write centroids to PDB
    n_clusters = len(centroids)
    with open(centroids_output_path, 'w') as f:
        for i, centroid in enumerate(centroids):
            writer(f, i + 1, centroid, norm_densities[i])


def calculate_matches(list_of_reports, atom_reports, atom_models, estimator,
                      results, ref_coords):
    """ It calculates the number of matches for each model sampled in the
    PELE simulation.

    PARAMETERS
    ----------
    list_of_reports : list
                      list of all the reports that were retrieved from the PELE
                      simulation that has been read.
    atom_reports : list
                   list of ordered atom reports.
    atom_models : list
                  list of ordered models.
    estimator : sklearn.cluster.MeanShift object
                clusterization implementation that clusterizes through the
                MeanShift method.
    results : list
              list with the results of the clusterization. Each element is the
              cluster in which each atom belongs.
    parsed_coords : list of floats
                    List of parsed 3D coordinates

    RETURNS
    -------
    matches_dict : dictionary of matches
                   dictionary that relates each Report object to the
                   corresponding number of matches.
    """

    def fulfill_condition(cluster_ids, reference_clusters):
        """ It checks if the match condition is fulfilled.

        PARAMETERS
        ----------
        cluster_ids : list of integers
                      water cluster ids
        reference_clusters : list of integers
                             list of reference cluster ids

        RETURNS
        -------
        matches : integer
                  number of matches that fulfill the matching condition.
        """
        copied_reference_clusters = copy(reference_clusters)
        common_matches = []

        for cluster_id in cluster_ids:
            if (cluster_id in copied_reference_clusters):
                copied_reference_clusters.remove(cluster_id)
                common_matches.append(cluster_id)

        return len(common_matches)

    # Assign clusters to reference coordinates
    reference_clusters = []
    for ref_coord in ref_coords:
        reference_clusters += estimator.predict([ref_coord]).tolist()

    # Initialize variables to compute matches
    clusters_dict = {}
    matches_dict = {}

    # Initialize matches_dict
    for report in list_of_reports:
        clusters_dict[report] = defaultdict(list)

    # Assign cluster ids
    for i, cluster_id in enumerate(results):
        clusters_dict[atom_reports[i]][atom_models[i]].append(cluster_id)

    # Compute matches and replace dictionary values for them
    for report, models in clusters_dict.items():
        matches_dict[report] = defaultdict(list)
        for model, cluster_ids in models.items():
            result = fulfill_condition(cluster_ids,
                                       reference_clusters)
            matches_dict[report][model] = result

    return matches_dict


def append_matches_to_reports(matches_dict, first_steps_to_ignore):
    """ It appends the number of matches to each PELE report.

    PARAMETERS
    ----------
    matches_dict : dictionary of matches
                   dictionary that relates each Report object to the
                   corresponding number of matches.
    first_steps_to_ignore : int
                            number of first steps that will be filtered out.


    """

    # Add matches to reports
    for report in matches_dict.keys():
        n_steps = report.getMetric(2)

        matches_to_add = []
        for n_step in n_steps:
            if (n_step < first_steps_to_ignore):
                matches_to_add.append(0)

        for model_num in sorted(matches_dict[report].keys()):
            matches_to_add.append(matches_dict[report][model_num])

        report.addMetric('WaterMatchs', matches_to_add)


def main():
    """Main function. It is called when this script is the main program
    called by the interpreter.
    """

    log = Logger()

    # Initial print
    log.info("+---------------------------------+")
    log.info("|    Water Clustering for PELE    |")
    log.info("+---------------------------------+")
    log.info("")

    # Parse command-line arguments
    control_file_path, number_of_processors, water_ids, ref_coords, \
        first_steps_to_ignore, cluster_radius, centroids_output_path, \
        normalize_densities = parseArgs()

    # Arguments validation
    log.info(' - Checking arguments')
    water_ids, number_of_processors = \
        arguments_validation(control_file_path,
                             number_of_processors,
                             water_ids)

    log.info(' - Retrieving water data from reports')
    # Get water data from reports
    (atom_reports, atom_ids, atom_models, atom_coords, atom_steps), \
        list_of_reports = obtain_water_data_from(control_file_path,
                                                 number_of_processors,
                                                 water_ids)

    log.info(' - Filtering structures')
    # Filter structures
    atom_reports, atom_ids, atom_models, atom_coords, atom_steps = \
        filter_structures(atom_reports,
                          atom_ids,
                          atom_models,
                          atom_coords,
                          atom_steps,
                          first_steps_to_ignore)

    log.info(' - Clustering using {} processors'.format(number_of_processors))
    estimator, results = clusterization(cluster_radius,
                                        number_of_processors,
                                        atom_coords)

    log.info(' - Calculating densities')
    densities = get_density(atom_ids, results, estimator, water_ids)

    log.info(' - Results')
    print_density_results(densities)

    log.info(' - Writing centroids')
    write_centroids(estimator, densities, centroids_output_path,
                    normalize_densities)

    if (ref_coords is not None):
        log.info(' - Calculating the number of matches for each model')
        append_matches_to_reports(calculate_matches(list_of_reports,
                                                    atom_reports,
                                                    atom_models,
                                                    estimator,
                                                    results,
                                                    ref_coords),
                                  first_steps_to_ignore)


if __name__ == "__main__":
    """Call the main function"""
    main()
