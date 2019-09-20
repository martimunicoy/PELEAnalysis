import os
from math import nan, isnan
from matplotlib import pyplot as plt
import seaborn as sns


PLOT_TYPES = ('ScatterPlot', 'InteractiveScatterPlot', 'DensityPlot', 'JointPlot')


class Plot(object):
    """Parent class that defines all basic parameters used in a PELE plot"""

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
        if (None in x_cols):
            x_cols = [2, ]
            x_name = "Pele step"
        if (None in y_cols):
            y_cols = [5, ]
            y_name = "Interaction energy ($kcal/mol$)"

        # Set plot axes
        self.axes = {'x': Axis(x_cols, x_name),
                     'y': Axis(y_cols, y_name),
                     'z': Axis(z_cols, z_name)}

        # Set other plot attributes
        self.output_path = output_path
        self.annotations = []
        self.z_max = z_max
        self.z_min = z_min

        # Set axis names
        for axis in self.axes.values():
            if (axis.name is None):
                axis.set_axis_name_from_report(reports[0])

        # Set axes values
        for rp in reports:
            report_directory = os.path.dirname(rp)
            report_number = os.path.basename(rp).split('_')[-1].split('.')[0]

            with open(rp, 'r') as rf:
                next(rf)
                for i, line in enumerate(rf):
                    for axis in self.axes.values():
                        if (axis.columns is None):
                            continue

                        total = 0.
                        for col in axis.columns:
                            try:
                                total += float(line.split()[col - 1])
                            except TypeError:
                                total = nan

                        if (isnan(total)):
                            print('Warning: incorrect data found at report ' +
                                  '{}, line {}'.format(rp, i))
                            continue

                        axis.add_value(total)

                    epoch = report_directory.split('/')[-1]
                    if (not epoch.isdigit()):
                        epoch = '0'

                    self.annotations.append(
                        "Epoch: " + epoch + "\n" +
                        "Trajectory: " + report_number + "\n" +
                        "Model: " + str(i + 1))

        if (self.axes['z'].values is not None):
            if (z_max is None):
                self.z_max = max(self.axes['z'].values)

            if (z_min is None):
                self.z_min = min(self.axes['z'].values)


class Axis(object):
    """This class handles data of a plot axis"""
    def __init__(self, axis_columns, axis_name=None):
        """Initializer function

        PARAMETERS
        ----------
        axis_columns : list of integers
                      list of column indexes from where to gather data in the
                      report. Note that report indexes start at 1. Also note
                      that in case that multiple indexes are defined here, the
                      final metric will be the sum of all the corresponding
                      metrics.
        axis_name : string
                    axis name
        """
        self._columns = axis_columns
        self.name = self._add_units(axis_name)
        self._values = []

    @property
    def columns(self):
        if (None in self._columns):
            return None

        return self._columns

    @property
    def values(self):
        if (len(self._values) == 0):
            return None

        return self._values

    def _add_units(self, metric_name):
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

        if (metric_name is None):
            return

        if ("energy" in metric_name.lower()):
            label = metric_name + " ($kcal/mol$)"
        elif ("energies" in metric_name.lower()):
            label = metric_name + " ($kcal/mol$)"
        elif ("distance" in metric_name.lower()):
            label = metric_name + " ($\AA$)"
        elif ("rmsd" in metric_name.lower()):
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
        if (self.columns is None):
            return

        with open(report, 'r') as report_file:
            line = report_file.readline()
            self.name = self._add_units(
                str(line.split("    ")[self.columns[0] - 1]))

    def clear_values(self):
        """It clears the values list of the axis
        """
        self._values = []

    def add_value(self, value):
        """Set axis name from report column info

        PARAMETERS
        ----------
        value : float
                Value that will be added to axis values list

        """
        self._values.append(value)


class ScatterPlot(Plot):
    """Scatter Plot class"""

    def __init__(self, reports, x_cols=[None, ], y_cols=[None, ],
                 z_cols=[None, ], x_name=None, y_name=None, z_name=None,
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
        super().__init__(reports, x_cols, y_cols, z_cols, x_name, y_name,
                         z_name, output_path, z_max, z_min)

        self.set_colormap('autumn')

    def set_colormap(self, colormap):
        """Set colormap of the plot

        PARAMETERS
        ----------
        colormap : string
                   name of the colormap to set
        """
        if (colormap == 'plasma'):
            self.cmap = plt.cm.plasma
        elif (colormap == 'autumn'):
            self.cmap = plt.cm.autumn
        elif (colormap == 'winter'):
            self.cmap = plt.cm.winter
        elif (colormap == 'spring'):
            self.cmap = plt.cm.spring
        elif (colormap == 'summer'):
            self.cmap = plt.cm.summer
        else:
            raise NameError('Unknown colormap name: \'{}\''.format(colormap))

    def show(self):
        """Display plot"""
        self._plot_builder()
        plt.show()

    def save_to(self, path):
        """Save the plot to a path

        PARAMETERS
        ----------
        path : string
               Path where the plot will be saved
        """
        self._plot_builder()
        plt.savefig(path)

    def _plot_builder(self):
        """Build the plot"""
        norm = plt.Normalize(self.z_min, self.z_max)

        fig, ax = plt.subplots()

        if (self.axes['z'].values is None):
            colors = [0 for i in range(0, len(self.axes['x'].values))]
        else:
            colors = self.axes['z'].values

        sc = plt.scatter(self.axes['x'].values,
                         self.axes['y'].values,
                         c=colors,
                         cmap=self.cmap, norm=norm)

        ax.margins(0.05)
        ax.set_facecolor('lightgray')
        plt.xlabel(self.axes['x'].name)
        plt.ylabel(self.axes['y'].name)

        # Activate the colorbar only if the Z axis contains data to plot
        if (self.axes['z'].values is not None):
            cbar = plt.colorbar(sc, drawedges=False)
            cbar.ax.set_ylabel(self.axes['z'].name)


class InteractiveScatterPlot(Plot):
    """Interactive Scatter Plot class"""

    def __init__(self, reports, x_cols=[None, ], y_cols=[None, ],
                 z_cols=[None, ], x_name=None, y_name=None, z_name=None,
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
        super().__init__(reports, x_cols, y_cols, z_cols, x_name, y_name,
                         z_name, output_path, z_max, z_min)

        self.set_colormap('autumn')

    def set_colormap(self, colormap):
        """Set colormap of the plot

        PARAMETERS
        ----------
        colormap : string
                   name of the colormap to set
        """
        if (colormap == 'plasma'):
            self.cmap = plt.cm.plasma
        elif (colormap == 'autumn'):
            self.cmap = plt.cm.autumn
        elif (colormap == 'winter'):
            self.cmap = plt.cm.winter
        elif (colormap == 'spring'):
            self.cmap = plt.cm.spring
        elif (colormap == 'summer'):
            self.cmap = plt.cm.summer
        else:
            raise NameError('Unknown colormap name: \'{}\''.format(colormap))

    def show(self):
        """Display plot"""
        self._plot_builder()
        plt.show()

    def save_to(self, path):
        """Save the plot to a path

        PARAMETERS
        ----------
        path : string
               Path where the plot will be saved
        """
        self._plot_builder()
        plt.savefig(path)

    def _plot_builder(self):
        """Build the plot"""
        norm = plt.Normalize(self.z_min, self.z_max)

        fig, ax = plt.subplots()

        if (self.axes['z'].values is None):
            colors = [0 for i in range(0, len(self.axes['x'].values))]
        else:
            colors = self.axes['z'].values

        sc = plt.scatter(self.axes['x'].values,
                         self.axes['y'].values,
                         c=colors,
                         cmap=self.cmap, norm=norm)

        ax.margins(0.05)
        ax.set_facecolor('lightgray')
        plt.xlabel(self.axes['x'].name)
        plt.ylabel(self.axes['y'].name)

        annot = ax.annotate("", xy=(0, 0), xytext=(20, 20),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        # Activate the colorbar only if the Z axis contains data to plot
        if (self.axes['z'].values is not None):
            cbar = plt.colorbar(sc, drawedges=False)
            cbar.ax.set_ylabel(self.axes['z'].name)

        def update_annot(ind):
            """Update the information box of the selected point"""
            pos = sc.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            annot.set_text(self.annotations[int(ind["ind"][0])])
            if (self.axes['z'].values is not None):
                annot.get_bbox_patch().set_facecolor(self.cmap(norm(
                    self.axes['z'].values[ind["ind"][0]])))

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


class DensityPlot(Plot):
    """Density Plot class"""

    def __init__(self, reports, x_cols=[None, ], y_cols=[None, ],
                 z_cols=[None, ], x_name=None, y_name=None, z_name=None,
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
        super().__init__(reports, x_cols, y_cols, z_cols, x_name, y_name,
                         z_name, output_path, z_max, z_min)

    def show(self):
        """Display plot"""
        self._plot_builder()
        plt.show()

    def save_to(self, path):
        """Save the plot to a path

        PARAMETERS
        ----------
        path : string
               Path where the plot will be saved
        """
        self._plot_builder()
        plt.savefig(path)

    def _plot_builder(self):
        f, ax = plt.subplots()

        ax = sns.kdeplot(self.axes['x'].values, self.axes['y'].values,
                         cmap="Reds", shade=True, shade_lowest=False)


class ScatterDensityPlot(Plot):
    """Scatter with denisty plot class"""

    def __init__(self, reports, x_cols=[None, ], y_cols=[None, ],
                 z_cols=[None, ], x_name=None, y_name=None, z_name=None,
                 output_path=None, z_max=None, z_min=None):
        """Initiate plot class

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
        super().__init__(reports, x_cols, y_cols, z_cols, x_name, y_name,
                         z_name, output_path, z_max, z_min)

        sns.set_style("ticks")

        self.color = 'blue'
        self.colors = {'blue': ('lightskyblue', 'royalblue'),
                       'red': ('lightcoral', 'firebrick'),
                       'green': ('palegreen', 'seagreen')}
        self.cmap = sns.dark_palette(self.colors[self.color][1], reverse=True,
                                     as_cmap=True)

        # Handle axes limits
        self._x_axis_limits = None
        self._y_axis_limits = None

        # Number of levels to plot
        self._n_levels = 5

        # Graph name
        self._name = ''

    @property
    def x_axis_limits(self):
        return self._x_axis_limits

    @property
    def y_axis_limits(self):
        return self._y_axis_limits

    @property
    def n_levels(self):
        return self._n_levels

    @property
    def name(self):
        return self._name

    def set_colormap(self, colormap):
        """Sets colormap

        PARAMETERS
        ----------
        colormap : string
                   name of the colormap
        """
        if (colormap in self.colors.keys()):
            self.color = colormap
        else:
            raise NameError('Unknown colormap name: \'{}\''.format(colormap))

    def set_x_axis_limits(self, limits):
        """Sets x axis limits

        PARAMETERS
        ----------
        limits : tuple of floats
                 axis limits
        """
        if (limits is not None):
            if (type(limits) != list and type(limits) != tuple):
                raise TypeError('Wrong limits format: \'{}\''.format(limits))
                if (len(limits != 2)):
                    raise TypeError('Wrong limits format: ' +
                                    '\'{}\''.format(limits))
        self._x_axis_limits = limits

    def set_y_axis_limits(self, limits):
        """Sets y axis limits

        PARAMETERS
        ----------
        limits : tuple of floats
                 axis limits
        """
        if (limits is not None):
            if (type(limits) != list and type(limits) != tuple):
                raise TypeError('Wrong limits format: \'{}\''.format(limits))
                if (len(limits != 2)):
                    raise TypeError('Wrong limits format: ' +
                                    '\'{}\''.format(limits))
        self._y_axis_limits = limits

    def set_n_levels(self, levels):
        """Sets number of levels to plot

        PARAMETERS
        ----------
        levels : integer
                 number of levels to plot
        """
        if (levels is not None):
            if (type(levels) != int):
                raise TypeError('Wrong number of levels: ' +
                                '\'{}\''.format(levels))
                if (levels < 1):
                    raise TypeError('Wrong number of levels: ' +
                                    '\'{}\''.format(levels))
        self._n_levels = levels

    def set_name(self, name):
        """Sets the name for the plot

        PARAMETERS
        ----------
        name : str
               name for the plot
        """
        self._name = name

    def show(self):
        """Display plot"""
        _ = self._plot_builder()
        plt.show()

    def save_to(self, path):
        """Save the plot to a path

        PARAMETERS
        ----------
        path : string
               Path where the plot will be saved
        """
        self._plot_builder()
        plt.savefig(path)

    def _plot_builder(self, display_edges=True):
        if (display_edges is False):
            edges_alpha = 0
            markers_alpha = 0.7
        else:
            edges_alpha = 1
            markers_alpha = 0.4

        ax = sns.jointplot(x=self.axes['x'].values, y=self.axes['y'].values,
                           color=self.colors[self.color][0],
                           kind='kde', cmap=self.cmap, shade=False,
                           n_levels=self.n_levels, alpha=edges_alpha)

        ax.plot_joint(sns.scatterplot, color=self.colors[self.color][0],
                      edgecolor=self.colors[self.color][1], marker='o',
                      alpha=markers_alpha, s=20)

        if (self.x_axis_limits is not None):
            ax.ax_marg_x.set_xlim(self.x_axis_limits[0], self.x_axis_limits[1])

        if (self.y_axis_limits is not None):
            ax.ax_marg_y.set_ylim(self.y_axis_limits[0], self.y_axis_limits[1])

        ax.set_axis_labels(self.axes['x'].name, self.axes['y'].name,
                           fontsize=16)

        return ax

    def show_joined(self, other_joint_plots):
        ax = self._plot_builder(display_edges=False)
        legends = [self.name, ]

        color, edgecolor = self.colors[self.color]

        sns.kdeplot(self.axes['x'].values, ax=ax.ax_marg_x,
                    color=color, shade=True, alpha=0.7)

        sns.kdeplot(self.axes['y'].values, ax=ax.ax_marg_y,
                    color=color, shade=True, vertical=True, alpha=0.7)

        for other_joint_plot in other_joint_plots:
            self._other_joint_plot(ax, other_joint_plot)
            legends.append(other_joint_plot.name)

        plt.legend(legends)

        plt.show()

    def _other_joint_plot(self, ax, other_joint_plot):
        ax.x = other_joint_plot.axes['x'].values
        ax.y = other_joint_plot.axes['y'].values
        color, edgecolor = self.colors[other_joint_plot.color]

        ax.plot_joint(sns.scatterplot, color=color, edgecolor=edgecolor,
                      marker='o', s=20)

        sns.kdeplot(other_joint_plot.axes['x'].values, ax=ax.ax_marg_x,
                    color=color, shade=True, alpha=0.7)

        sns.kdeplot(other_joint_plot.axes['y'].values, ax=ax.ax_marg_y,
                    color=color, shade=True, vertical=True, alpha=0.7)
