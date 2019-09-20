# -*- coding: utf-8 -*-


# Imports
from __future__ import unicode_literals
import os
import glob
import argparse as ap
from matplotlib import pyplot
from math import isnan


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Functions
def parseReports(reports_to_parse, parser=None):
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

    if (parser is not None):
        if len(reports) == 0:
            print("Error: list of report files is empty.")
            parser.print_help()
            exit(1)

    return reports


def parseArgs():
    """Parse arguments from command-line

    RETURNS
    -------
    reports : string
              list of report files to look for data
    x_data : string
             data to parse and assign to the X axis
    y_data : string
             data to parse and assign to the Y axis
    z_data : string
             data to parse and assign to the colorbar
    z_max : float
            it sets the maximum range value of the colorbar
    z_min : float
            it sets the minimum range value of the colorbar
    output_path : string
                  output directory where the resulting plot will be saved
    """

    parser = ap.ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, metavar="FILE",
                          type=str, nargs='*', help="path to report files")
    optional.add_argument("-X", "--xaxis", metavar="INTEGER [METRIC]",
                          type=str, nargs='*', help="column numbers and " +
                          "metric to plot on the X axis", default=None)
    optional.add_argument("-Y", "--yaxis", metavar="INTEGER [METRIC]",
                          type=str, nargs='*', help="column numbers and " +
                          "metric to plot on the Y axis", default=None)
    optional.add_argument("-Z", "--zaxis", metavar="INTEGER [METRIC]",
                          type=str, nargs='*', help="column numbers and " +
                          "metric to represent in the colorbar", default=None)
    optional.add_argument("-o", "--output", metavar="PATH", type=str,
                          help="output path to save figure", default=None)
    optional.add_argument("-r", "--Zmin", metavar="FLOAT", type=float,
                          help="minimum Z value for the colorbar",
                          default=None)
    optional.add_argument("-R", "--Zmax", metavar="FLOAT", type=float,
                          help="maximum Z value for the colorbar",
                          default=None)
    parser._action_groups.append(optional)
    args = parser.parse_args()

    reports = parseReports(args.input, parser)

    x_data = args.xaxis
    y_data = args.yaxis
    z_data = args.zaxis

    if z_data is None:
        if args.Zmin is not None or args.Zmax is not None:
            print("No data to represent in the colorbar (Z axis). " +
                  "Custom ranges are ignored.")
        z_min = None
        z_max = None
    else:
        z_min = args.Zmin
        z_max = args.Zmax

    output_path = args.output

    return reports, x_data, y_data, z_data, z_min, z_max, output_path


def addUnits(metric_name):
    """Add units according to the input metric

    PARAMETERS
    ----------
    metric_name : string
                  name of the metric to plot

    RETURNS
    -------
    label : string
            name of the metric to plot with the units that were added to it
    """

    if "energy" in metric_name.lower():
        label = metric_name + " ($kcal/mol$)"
    elif "energies" in metric_name.lower():
        label = metric_name + " ($kcal/mol$)"
    elif "distance" in metric_name.lower():
        label = metric_name + " ($\AA$)"
    elif "rmsd" in metric_name.lower():
        label = metric_name + " ($\AA$)"
    else:
        label = metric_name
    return label


def parseAxisData(axis_data):
    """It sets the columns and label of the data that wants to be plotted

    PARAMETERS
    ----------
    axis_data : string
                axis data to parse

    RETURNS
    -------
    parsed_data : tuple of a list and a string
                  the list specifies the report columns that want to be plotted
                  in the axis and the string sets the name of the axis
    """

    if axis_data is None:
        return ([None, ], None)
    else:
        try:
            rows = [int(axis_data[0]), ]
        except ValueError:
            print("Warning: axis data not recognized: {}".format(axis_data))
            return ([None, ], None)
        if len(axis_data) == 1:
            return (rows, None)
        elif len(axis_data) > 1:
            label_index = 1
            while axis_data[label_index] == "+":
                label_index += 2
                try:
                    rows.append(int(axis_data[2]))
                except (ValueError, IndexError):
                    print("Warning: axis data not recognized: " +
                          "{}".format(axis_data))
                    return ([None, ], None)
                if len(axis_data) == label_index:
                    return (rows, '?')
            label = addUnits(axis_data[label_index])
            return (rows, label)

        print("Warning: axis data not recognized: {}".format(axis_data))
        return ([None, ], None)


def scatterPlot(reports,
                x_rows=[None, ], y_rows=[None, ], z_rows=[None, ],
                x_name=None, y_name=None, z_name=None,
                output_path=None, z_max=None, z_min=None):
    """Represent the scatter plot

    PARAMETERS
    ----------
    reports : string
              list of report files to look for data
    x_rows : list of integers
             integers which specify the report columns to represent in the X
             axis
    y_rows : list of integers
             integers which specify the report columns to represent in the Y
             axis
    z_rows : list of integers
             integers which specify the report columns to represent in the
             colorbar
    x_name : string
             label of the X axis
    y_name : string
             label of the Y axis
    z_name : string
             label of the colorbar
    output_path : string
                  output directory where the resulting plot will be saved
    z_max : float
            it sets the maximum range value of the colorbar
    z_min : float
            it sets the minimum range value of the colorbar
    """
    x_values = []
    y_values = []
    z_values = []
    labels = []
    annotations = []

    with open(reports[0], 'r') as report_file:
        line = report_file.readline()
        if None in x_rows:
            x_rows = [7, ]
            x_name = "RMSD ($\AA$)"
        if None in y_rows:
            y_rows = [5, ]
            y_name = "Energy ($kcal/mol$)"
        if x_name is None:
            x_name = str(line.split("    ")[x_rows[0] - 1])
        if y_name is None:
            y_name = str(line.split("    ")[y_rows[0] - 1])
        if (None not in z_rows) and (z_name is None):
            z_name = str(line.split("    ")[z_rows[0] - 1])
            z_name = addUnits(z_name)

    for report in reports:
        report_directory = os.path.dirname(report)
        report_number = os.path.basename(report).split('_')[-1].split('.')[0]

        with open(report, 'r') as report_file:
            next(report_file)
            for i, line in enumerate(report_file):
                x_total = 0.
                y_total = 0.
                z_total = 0.

                for x_row in x_rows:
                    x_total += float(line.split()[x_row - 1])

                for y_row in y_rows:
                    y_total += float(line.split()[y_row - 1])

                if None not in z_rows:
                    for z_row in z_rows:
                        z_total += float(line.split()[z_row - 1])

                if isnan(x_total) or isnan(y_total) or isnan(z_total):
                    continue

                x_values.append(x_total)
                y_values.append(y_total)
                z_values.append(z_total)

                epoch = report_directory.split('/')[-1]
                if not epoch.isdigit():
                    epoch = '0'

                annotations.append("Epoch: " + epoch + "\n" +
                                   "Trajectory: " + report_number + "\n" +
                                   "Model: " + str(i + 1))

                labels.append(0)

    if z_max is None:
        z_max = max(z_values)

    if z_min is None:
        z_min = min(z_values)

    if z_min == z_max:
        cmap = pyplot.cm.autumn
    else:
        cmap = pyplot.cm.plasma

    norm = pyplot.Normalize(z_min, z_max)

    fig, ax = pyplot.subplots()

    if output_path is not None:
        s = 20
    else:
        s = None

    sc = pyplot.scatter(x_values, y_values, c=z_values, cmap=cmap, s=s,
                        norm=norm)

    ax.margins(0.05)
    ax.set_facecolor('lightgray')
    pyplot.ylabel(y_name)
    pyplot.xlabel(x_name)

    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    # Activate the colorbar only if the Z axis contains data to plot
    if None not in z_rows:
        cbar = pyplot.colorbar(sc, drawedges=False)
        cbar.ax.set_ylabel(z_name)

    def update_annot(ind):
        """Update the information box of the selected point"""
        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        annot.set_text(annotations[int(ind["ind"][0])])
        annot.get_bbox_patch().set_facecolor(cmap(norm(
            z_values[ind["ind"][0]])))

    def hover(event):
        """Action to perform when hovering the mouse on a point"""
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    # Respond to mouse motion
    fig.canvas.mpl_connect("motion_notify_event", hover)

    # Save or display the plot depending on whether an output path was set or
    # not
    if output_path is not None:
        pyplot.savefig(output_path)
    else:
        pyplot.show()


def main():
    """Main function

    It is called when this script is the main program called by the interpreter
    """

    # Parse command-line arguments
    reports, x_data, y_data, z_data, z_min, z_max, output_path = parseArgs()

    # Parse axis data to label it properly
    x_rows, x_name = parseAxisData(x_data)
    y_rows, y_name = parseAxisData(y_data)
    z_rows, z_name = parseAxisData(z_data)

    # Generate the plot
    scatterPlot(reports,
                x_rows=x_rows, y_rows=y_rows, z_rows=z_rows,
                x_name=x_name, y_name=y_name, z_name=z_name,
                z_min=z_min, z_max=z_max,
                output_path=output_path)


if __name__ == "__main__":
    """Call the main function"""
    main()
