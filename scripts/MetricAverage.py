# -*- coding: utf-8 -*-


# Imports
from __future__ import unicode_literals
import glob
import argparse as ap
from numpy import mean
from math import isnan


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Functions
def parseReports(reports_to_parse, parser):
    """It identifies the reports to add to the plot

    PARAMETERS
    ----------
    reports_to_parse : list of strings
                       all the report files that want to be added to the plot
    parser : ArgumentParser object
             contains information about the command line arguments

    RETURNS
    -------
    parsed_data : tuple of a list and a string
                  the list specifies the report columns that want to be plotted
                  in the axis and the string sets the name of the axis
    """

    reports = []

    for reports_list in reports_to_parse:
        trajectories_found = glob.glob(reports_list)
        if len(trajectories_found) == 0:
            print("Warning: path to report file \'" +
                  "{}".format(reports_list) + "\' not found.")
        for report in glob.glob(reports_list):
            reports.append(report)

    if len(reports) == 0:
        print "Error: list of report files is empty."
        parser.print_help()
        exit(1)

    return reports


def parseArgs():
    """Parse arguments from command-line

    RETURNS
    -------
    reports : string
              list of report files to look for data
    colnum : int
             column number that
    """

    parser = ap.ArgumentParser()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, metavar="FILE",
                          type=str, nargs='*', help="path to report files")
    required.add_argument("-c", "--column", required=True, metavar="INTEGER",
                          type=int, help="column number of the metric that " +
                          "wants to be averaged", default=None)

    args = parser.parse_args()

    reports = parseReports(args.input, parser)

    colnum = args.column

    return reports, colnum


def readMetricFromReports(reports, colnum):
    metric_list = []
    for report in reports:
        with open(report, 'r') as report_file:
            next(report_file)
            for line in report_file:
                value = float(line.split()[colnum - 1])
                if not isnan(value) or value > -1000.:
                    metric_list.append(value)

    return metric_list


def meanMetric(metric_list):
    return mean(metric_list)


def main():
    """Main function

    It is called when this script is the main program called by the interpreter
    """

    # Parse command-line arguments
    reports, colnum = parseArgs()

    # Get list of all metric's values from report files
    metric_list = readMetricFromReports(reports, colnum)

    # Calculate mean
    mean = meanMetric(metric_list)

    # Print results
    print(mean)


if __name__ == "__main__":
    """Call the main function"""
    main()
