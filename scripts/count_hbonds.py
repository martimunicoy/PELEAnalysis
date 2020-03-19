import pandas as pd
import matplotlib.pyplot as plt

REP_FILE = "/home/carles/report_example.txt"


def create_df(report_file):
    rows_df = {}
    with open(report_file) as in_file:
        rows = in_file.readlines()
        for n, row in enumerate(rows):
            rows_df[n] = row.split()
    return rows_df


def get_atoms_from_df(df_dict):
    all_res = []
    for inx, row in df_dict.items():
        residues = row[3].split(",")[:-1]
        for residue in residues:
            all_res.append(residue)
    return all_res


def get_residues_from_df(df_dict):
    all_res = []
    for inx, row in df_dict.items():
        residues = row[3].split(",")[:-1]
        for residue in residues:
            all_res.append(residue.split("-")[-0])
    return all_res


def count_residues(residue_list):
    counts = {}
    for res in residue_list:
        counts[res] = counts.get(res, 0) + 1
    return counts


def create_barplot(dictionary):
    plt.bar(sorted(range(len(dictionary))), sorted(list(dictionary.values())), align='center')
    plt.xticks(sorted(range(len(dictionary))), sorted(list(dictionary.keys())))


def main(report_file):
    df = create_df(report_file)
    residues = get_residues_from_df(df)
    counting = count_residues(residues)
    create_barplot(counting)
    plt.show()

main(REP_FILE)
