from multiprocessing import Pool
from copy import copy
from functools import partial

from PELETools import ControlFileParser as cfp
from PELETools import SimulationParser as sp


def obtain_water_data_from(control_file_path, number_of_processors,
                           water_simulation_ids, first_atoms_to_ignore):
    print('- Parsing control file...')
    builder = cfp.ControlFileBuilder(control_file_path)
    cf = builder.build()
    sim = cf.getSimulation()

    print('- Listing reports...')
    list_of_reports = []
    for report in sim.iterateOverReports:
        list_of_reports.append(report)
       
    if (len(water_simulation_ids) == 0):
        return (None, None, None, None), list_of_reports

    print('- Retrieving data...')
    parallel_function = partial(parallel_atom_getter, water_simulation_ids,
                                first_atoms_to_ignore)
    with Pool(number_of_processors) as pool:
        atom_data = pool.map(parallel_function, list_of_reports)

    fixed_atom_data = []

    print('- Linking report pointers...')
    for (path, name), atom_coords in atom_data:
        for report in list_of_reports:
            if ((report.path, report.name) == (path, name)):
                report_pointer_to_add = report
                break
        else:
            raise NameError("Report {}{} not found".format(path, name))
        fixed_atom_data.append((report_pointer_to_add, atom_coords))

    print('- Parsing data...')
    return split_atom_data(fixed_atom_data), list_of_reports


def parallel_atom_getter(water_simulation_ids, first_atoms_to_ignore, report):
    atom_coords = {}
    for i, water_id in enumerate(water_simulation_ids):
        atoms = report.trajectory.getAtoms(water_id)
        for j, atom in enumerate(atoms[first_atoms_to_ignore:]):
            atom_coords[(i, j + first_atoms_to_ignore)] = atom.coords

    atom_data = ((report.path, report.name), atom_coords)
    return atom_data


def split_atom_data(atom_data):
    atom_reports = []
    atom_ids = []
    atom_models = []
    atom_coords = []

    for data in atom_data:
        for (water_id, model), coords in data[1].items():
            atom_reports.append(data[0])
            atom_ids.append(water_id)
            atom_models.append(model)
            atom_coords.append(coords)

    return atom_reports, atom_ids, atom_models, atom_coords


def get_reference_coords(reference_pdb_name, path, water_reference_ids):
    reference = sp.Trajectory(reference_pdb_name, path, None, 0, 0, 0)

    ref_coords = []
    for water_id in water_reference_ids:
        ref_coords.append(reference.getAtoms(water_id)[0].coords)

    return ref_coords


def get_density(atom_ids, results, water_simulation_ids):
    n_clusters = int(max(results) + 1)

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


def get_metric(list_of_reports, first_atoms_to_ignore, col_num=None,
               metric_name=None):
    if (col_num is None and metric_name is None):
        raise NameError(
            "Either column number or metric name must be especified")

    # Get metrics
    metric_values = []

    for report in list_of_reports:
        metric_values += report.getMetric(col_num,
                                          metric_name)[first_atoms_to_ignore:]

    return metric_values


def get_ordered_matchs(list_of_reports, matchs_dict, reference_matchs,
                       min_matchs_tofulfill=None):
    matchs = []

    for report in list_of_reports:
        for model_num in sorted(matchs_dict[report].keys()):
            matchs.append(fulfill_condition(matchs_dict[report][model_num],
                          reference_matchs, min_matchs_tofulfill))

    return matchs


def add_matchs_to_reports(list_of_reports, matchs, first_atoms_to_ignore):
    index = 0
    for report in list_of_reports:
        matchs_to_add = [0, ] * first_atoms_to_ignore
        for model in range(first_atoms_to_ignore, report.trajectory.models.number):
            matchs_to_add.append(matchs[index])
            index += 1
        report.addMetric('WaterMatchs', matchs_to_add)


def get_matchs(list_of_reports, results, atom_reports, atom_models,
               first_atoms_to_ignore):
    matchs = {}

    # Initialize matchs_dict
    for report in list_of_reports:
        matchs[report] = {}
        for model in range(first_atoms_to_ignore,
                           report.trajectory.models.number):
            matchs[report][model] = []

    for i, cluster_id in enumerate(results):
        matchs[atom_reports[i]][atom_models[i]].append(cluster_id)

    return matchs


def fulfill_condition(matchs, reference_matchs, min_matchs_to_fulfill=None):
    if (min_matchs_to_fulfill is None):
        min_matchs_to_fulfill = len(reference_matchs)

    copied_reference_matchs = copy(reference_matchs)
    common_matchs = []

    for match in matchs:
        if match in copied_reference_matchs:
            copied_reference_matchs.remove(match)
            common_matchs.append(match)

    return len(common_matchs)


def write_centroids(estimator, densities=None, output_name='centroid.pdb',
                    normalize=False):
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
    with open(output_name, 'w') as f:
        for i, centroid in enumerate(centroids):
            writer(f, i + 1, centroid, norm_densities[i])
