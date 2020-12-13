# -*- coding: utf-8 -*-


import argparse as ap
import glob
from tqdm import tqdm


def parse_reports(reports_to_parse, parser=None):
    """
    It identifies the reports to analyze

    Parameters
    ----------
    reports_to_parse : list of strings
                       all the report files that want to be added to the plot
    parser : ArgumentParser object
             contains information about the command line arguments

    Returns
    -------
    parsed_data : tuple of a list and a string
                  the list specifies the report columns that want to be plotted
                  in the axis and the string sets the name of the axis
    """

    reports = []

    for reports_list in reports_to_parse:
        trajectories_found = glob.glob(reports_list)
        if len(trajectories_found) == 0:
            print("Warning: path to report file \'"
                  + "{}".format(reports_list) + "\' not found.")
        for report in glob.glob(reports_list):
            reports.append(report)

    if (parser is not None):
        if len(reports) == 0:
            print("Error: list of report files is empty.")
            parser.print_help()
            exit(1)

    return reports


def main():
    parser = ap.ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("report_paths", metavar="FILE",
                          type=str, nargs='*', help="path to report files")
    optional.add_argument("-c", "--column", metavar="INT", type=int,
                          help="the metric column to split",
                          default=7)
    optional.add_argument("-t", "--threshold", metavar="FLOAT", type=float,
                          help="threshold value",
                          default=1.0)

    parser._action_groups.append(optional)
    args = parser.parse_args()

    reports = parse_reports(args.report_paths)
    column = args.column
    threshold = args.threshold

    if column < 1:
        raise ValueError('Column index must start at 1.')

    lower_counter = 0
    upper_counter = 0

    for report in tqdm(reports):
        with open(report, 'r') as report_file:
            next(report_file)
            for i, line in enumerate(report_file, start=2):
                fields = line.split()
                if column > len(fields):
                    raise ValueError('Invalid selected column, '
                                     + 'number of fields in line '
                                     + '{} '.format(i)
                                     + 'of report {} '.format(report)
                                     + 'is lower than the selected '
                                     + 'column: {} '.format(column)
                                     + '> {}'.format(len(fields)))
                value = float(fields[column - 1])
                if value <= threshold:
                    lower_counter += 1
                else:
                    upper_counter += 1

    total = lower_counter + upper_counter

    if total == 0:
        raise Exception('No entry was found in the supplied path')

    print(' - Counter results:')
    print('   - Total entries: {:10d}'.format(total))
    print('   - Below {:7.2f}: {:10d} ({:5.1f}%)'.format(
        threshold, lower_counter, lower_counter / total * 100))
    print('   - Above {:7.2f}: {:10d} ({:5.1f}%)'.format(
        threshold, upper_counter, upper_counter / total * 100))


if __name__ == '__main__':
    main()
