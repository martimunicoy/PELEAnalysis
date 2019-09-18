import os
from math import isnan


class Plot(object):
    """ Parent class that defines all basic parameters used in a PELE plot"""

    def __init__(self, reports,
                 x_cols=[None, ], y_cols=[None, ], z_cols=[None, ],
                 x_name=None, y_name=None, z_name=None,
                 output_path=None, z_max=None, z_min=None):
        """Represent the scatter plot

        PARAMETERS
        ----------
        reports : string
                  list of report files to look for data
        x_cols : list of integers
                 integers which specify the report columns to represent in the
                 X axis
        y_cols : list of integers
                 integers which specify the report columns to represent in the
                 Y axis
        z_cols : list of integers
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

        # Set default x and y axis
        if (None in self.x_rows):
            self.x_cols = [2, ]
            self.x_name = "Pele step"
        if (None in self.y_rows):
            self.y_cols = [5, ]
            self.y_name = "Interaction energy ($kcal/mol$)"

        # Set plot axes
        self.axes = {'x': Axis(x_cols, x_name),
                     'y': Axis(y_cols, y_name),
                     'z': Axis(z_cols, z_name)}

        # Set other plot attributes
        self.output_path = output_path

        for axis in self.axes.values():
            if (axis.axis_name is None):
                self.x_axis.set_axis_name_from_report(reports[0])

        self.x_axis.get_values_from_reports(reports)



class Axis(object):
    """ This class handles data of a plot axis """
    def __init__(self, axis_columns, axis_name=None):
        """Initializer function

        PARAMETERS
        ----------
        axis_column : list of integers
                      list of column indexes from where to gather data in the
                      report. Note that report indexes start at 1. Also note
                      that in case that multiple indexes are defined here, the
                      final metric will be the sum of all the corresponding
                      metrics.
        axis_name : string
                    axis name
        """
        self.axis_column = axis_columns
        self.axis_name = self._add_units(axis_name)
        self._values = []

    @property
    def values(self):
        return self._values

    def _add_units(metric_name):
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

    def set_axis_name_from_report(self, report):
        """Set axis name from report column info

        PARAMETERS
        ----------
        report : string
                 path to PELE report from where to extract axis name

        """
        with open(report, 'r') as report_file:
            line = report_file.readline()
            self.axis_name = str(line.split("    ")[self.axis_column[0] - 1])

    def set_values_from_reports(self, reports):
        """Set axis name from report column info

        PARAMETERS
        ----------
        reports : list of strings
                  list of paths to PELE report from where to extract axis
                  values

        """
        self._values = []

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




class scatterPlot(object):



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