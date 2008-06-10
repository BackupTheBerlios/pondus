#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This file is part of Pondus, a personal weight manager.
Copyright (C) 2007-08  Eike Nicklas <eike@ephys.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import timedelta
from matplotlib.figure import Figure
from matplotlib import dates

from pondus import datasets
from pondus import parameters
from pondus.core import util


class Plot(object):
    """Describes the plot figure and implements methods to modify it."""
    def __init__(self):
        """Plots the weight data vs time."""
        self.mindate = None
        self.maxdate = None
        self.plot_plan = parameters.config['preferences.use_weight_plan'] \
                and parameters.config['preferences.plot_weight_plan']
        self.plot_data_meas = get_plot_data(datasets.all_datasets)
        if self.plot_plan:
            self.plot_data_plan = get_plot_data(datasets.plan_datasets)
        else:
            self.plot_data_plan = []
        self.create_plot()

    def set_daterange(self, mindate, maxdate):
        """Sets the desired daterange of the plot."""
        self.mindate = mindate
        self.maxdate = maxdate

    def create_plot(self):
        """Creates the plot and basic formatting."""
        xlist_meas = [tup[0] for tup in self.plot_data_meas]
        ylist_meas = [tup[1] for tup in self.plot_data_meas]
        xlist_plan = [tup[0] for tup in self.plot_data_plan]
        ylist_plan = [tup[1] for tup in self.plot_data_plan]
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        if len(xlist_meas) != 0:
            self.ax.plot_date(dates.date2num(xlist_meas), ylist_meas, \
                            fmt='bo-', ms=4.0)
        if len(xlist_plan) != 0 and self.plot_plan:
            self.ax.plot_date(dates.date2num(xlist_plan), ylist_plan, \
                            fmt='ro-', ms=4.0)
        ylabel = _('Weight') + ' (' \
                + parameters.config['preferences.weight_unit'] + ')'
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)

    def format_plot(self):
        """Formats the plot, i.e. sets limits, ticks, etc."""
        daterange = self.maxdate - self.mindate
        majorlocator, majorformatter, minorlocator = get_locators(daterange)

        y_min, y_max = self.get_yrange()
        if y_min is not None:
            self.ax.set_ylim(y_min, y_max)

        self.ax.set_xlim(dates.date2num(self.mindate), \
                         dates.date2num(self.maxdate))
        self.ax.xaxis.set_major_locator(majorlocator)
        self.ax.xaxis.set_major_formatter(majorformatter)
        self.ax.xaxis.set_minor_locator(minorlocator)

    def update_plot(self, mindate, maxdate):
        """Updates the plot formatting and redraws the plot."""
        self.set_daterange(mindate, maxdate)
        self.format_plot()
        self.figure.canvas.draw()

    def save_to_file(self, filename):
        """Saves the plot to filename. The filename's ending must be
        a valid format to save to."""
        print _('Saving plot to'), filename
        self.figure.savefig(filename, format=filename[-3:])

    def get_yrange(self):
        """Returns the minimum and the maximum y-value in the given date
        range."""
        y_offset = 0.5
        y_min_meas, y_max_meas = self.get_yrange_data(self.plot_data_meas)
        y_min_plan, y_max_plan = self.get_yrange_data(self.plot_data_plan)
        y_min, y_max = util.compare_with_possible_nones( \
            y_min_meas, y_max_meas, y_min_plan, y_max_plan)
        # y_min, y_max can be None if no datasets in selected daterange
        if y_min is not None:
            y_min -= y_offset
            y_max += y_offset
        return y_min, y_max

    def get_yrange_data(self, datasets):
        """Returns the minimum and the maximum y-value in the plot data.
        Returns None, None if no measurements exist in the chosen date
        range."""
        try:
            minweight = min(dataset[1] \
                for dataset in datasets \
                if self.mindate <= dataset[0] <= self.maxdate)
            maxweight = max(dataset[1] \
                for dataset in datasets \
                if self.mindate <= dataset[0] <= self.maxdate)
            return minweight, maxweight
        except ValueError:
            return None, None

    def get_max_daterange(self):
        """Returns the minimum and the maximum date in the available
        data. Returns None, None if no measurements exist."""
        try:
            mindate_meas = self.plot_data_meas[0][0]
            maxdate_meas = self.plot_data_meas[-1][0]
        except IndexError:
            mindate_meas = None
            maxdate_meas = None
        try:
            mindate_plan = self.plot_data_plan[0][0]
            maxdate_plan = self.plot_data_plan[-1][0]
        except IndexError:
            mindate_plan = None
            maxdate_plan = None
        mindate, maxdate = util.compare_with_possible_nones( \
            mindate_meas, maxdate_meas, mindate_plan, maxdate_plan)
        return mindate, maxdate

def get_plot_data(datasets):
    """Returns the datalists to be plotted."""
    data = [(dataset.get('date'), dataset.get('weight')) \
            for dataset in datasets]
    data.sort()
    return data

def get_locators(daterange):
    """Returns sane locators and formatters for the given
    daterange."""
    if daterange >= timedelta(days=8000):
        majorlocator = dates.YearLocator(10)
        majorformatter = dates.DateFormatter("%Y")
        minorlocator = dates.YearLocator(2)
    elif daterange >= timedelta(days=4000):
        majorlocator = dates.YearLocator(2)
        majorformatter = dates.DateFormatter("%Y")
        minorlocator = dates.YearLocator()
    elif daterange >= timedelta(days = 700):
        majorlocator = dates.YearLocator()
        majorformatter = dates.DateFormatter("%Y")
        minorlocator = dates.MonthLocator(bymonth=(1, 4, 7, 10))
    elif daterange >= timedelta(days = 200):
        majorlocator = dates.MonthLocator(bymonth=(1, 4, 7, 10))
        majorformatter = dates.DateFormatter("%b %Y")
        minorlocator = dates.MonthLocator()
    elif daterange >= timedelta(days = 50):
        majorlocator = dates.MonthLocator()
        majorformatter = dates.DateFormatter("%b %Y")
        minorlocator = dates.WeekdayLocator(byweekday=6)
    else:
        majorlocator = dates.WeekdayLocator(byweekday=6)
        majorformatter = dates.DateFormatter("%d %b")
        minorlocator = dates.DayLocator()
    return majorlocator, majorformatter, minorlocator
