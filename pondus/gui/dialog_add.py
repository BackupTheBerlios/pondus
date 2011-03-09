# -*- coding: UTF-8 -*-

"""
This file is part of Pondus, a personal weight manager.
Copyright (C) 2007-11  Eike Nicklas <eike@ephys.de>

This program is free software licensed under the MIT license. For details
see LICENSE or http://www.opensource.org/licenses/mit-license.php
"""

import gtk
import gobject
from datetime import date, timedelta

from pondus.core import parameters
from pondus.core import util
from pondus.gui.dialog_message import MessageDialog


class AddDataDialog(object):
    """Implements the user interface to add or edit datasets."""

    def __init__(self, parent_window, dataset, edit):
        self.dataset = dataset
        # get default values for entry boxes
        if parameters.config['preferences.unit_system'] == 'imperial':
            weight = self.dataset.weight_lbs
        else:
            weight = self.dataset.weight
        if parameters.config['preferences.use_bodyfat']:
            bodyfat = self.dataset.bodyfat
            if bodyfat is None:
                bodyfat = 0.0
        if parameters.config['preferences.use_note']:
            note = self.dataset.note
            if note is None:
                note = ''

        self.dialog = gtk.Dialog(parent=parent_window,
                                flags=gtk.DIALOG_NO_SEPARATOR)
        # set the title
        if edit:
            self.dialog.set_title(_('Edit Dataset'))
        else:
            self.dialog.set_title(_('Add Dataset'))

        # create the labels and entry boxes
        date_box = gtk.VBox(spacing=5)
        date_box.set_border_width(5)
        if parameters.config['preferences.use_calendar']:
            date_ = self.dataset.date
            date_label = gtk.Label(_('Date:'))
            date_label.set_alignment(xalign=0, yalign=0.5)
            self.calendar = gtk.Calendar()
            if parameters.config['preferences.unit_system'] == 'metric':
                self.calendar.set_display_options(
                                            gtk.CALENDAR_SHOW_HEADING |
                                            gtk.CALENDAR_SHOW_DAY_NAMES |
                                            gtk.CALENDAR_WEEK_START_MONDAY)
            self.calendar.select_month(date_.month-1, date_.year)
            self.calendar.select_day(date_.day)
            date_box.pack_start(date_label)
            date_box.pack_start(self.calendar)
        else:
            date_ = str(self.dataset.date)
            date_label = gtk.Label(_('Date (YYYY-MM-DD):'))
            date_label.set_alignment(xalign=0, yalign=0.5)
            self.date_entry = gtk.Entry()
            self.date_entry.set_text(date_)
            self.date_entry.set_activates_default(True)
            date_box.pack_start(date_label)
            date_box.pack_start(self.date_entry)

        weight_box = gtk.VBox(spacing=5)
        weight_box.set_border_width(5)
        weight_label = gtk.Label(
                (_('Weight') + ' (' + util.get_weight_unit() + '):'))
        weight_label.set_alignment(xalign=0, yalign=0.5)
        weight_adj = gtk.Adjustment(value=weight, lower=0, upper=1000,
                                    step_incr=0.1, page_incr=1.0)
        self.weight_entry = gtk.SpinButton(adjustment=weight_adj, digits=1)
        self.weight_entry.set_numeric(True)
        self.weight_entry.set_activates_default(True)
        weight_box.pack_start(weight_label)
        weight_box.pack_start(self.weight_entry)

        self.dialog.vbox.pack_start(date_box)
        self.dialog.vbox.pack_start(weight_box)


        if parameters.config['preferences.use_bodyfat']:
            bodyfat_box = gtk.VBox(spacing=5)
            bodyfat_box.set_border_width(5)
            bodyfat_label = gtk.Label(_('Bodyfat (%):'))
            bodyfat_label.set_alignment(xalign=0, yalign=0.5)
            bodyfat_adj = gtk.Adjustment(value=bodyfat, lower=0, upper=100,
                                        step_incr=0.1, page_incr=1.0)
            self.bodyfat_entry = gtk.SpinButton(adjustment=bodyfat_adj,
                                                digits=1)
            self.bodyfat_entry.set_numeric(True)
            self.bodyfat_entry.set_activates_default(True)
            bodyfat_box.pack_start(bodyfat_label)
            bodyfat_box.pack_start(self.bodyfat_entry)
            self.dialog.vbox.pack_start(bodyfat_box)

        if parameters.config['preferences.use_note']:
            note_box = gtk.VBox(spacing=5)
            note_box.set_border_width(5)
            textwindow = gtk.ScrolledWindow()
            textwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            note_label = gtk.Label(_('Note:'))
            note_label.set_alignment(xalign=0, yalign=0.5)
            self.note_view = gtk.TextView()
            self.note_view.set_editable(True)
            self.note_view.set_wrap_mode(gtk.WRAP_WORD)
            self.note_buffer = self.note_view.get_buffer()
            self.note_buffer.set_text(note)
            textwindow.add(self.note_view)
            note_box.pack_start(note_label)
            note_box.pack_start(textwindow)
            self.dialog.vbox.pack_start(note_box)

        # buttons in action area
        self.dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)

        self.dialog.set_default_response(gtk.RESPONSE_OK)

        # connect the signals
        self.weight_insert_signal = \
                self.weight_entry.connect('insert_text', self.on_insert)
        if not parameters.config['preferences.use_calendar']:
            self.date_entry.connect('focus-in-event', self.on_focus)
            self.date_insert_signal = \
                    self.date_entry.connect('insert_text', self.on_insert)

        # show the content
        self.dialog.show_all()

    def run(self):
        """Runs the dialog and returns the new/updated dataset."""
        response = self.dialog.run()
        if response == gtk.RESPONSE_OK:
            # try to create a new dataset from the given data
            try:
                if parameters.config['preferences.use_calendar']:
                    updated_year, updated_month, updated_day = \
                            self.calendar.get_date()
                    self.dataset.date = \
                            date(updated_year, updated_month+1, updated_day)
                else:
                    self.dataset.date = \
                            util.str2date(self.date_entry.get_text())
                if parameters.config['preferences.unit_system'] == 'imperial':
                    self.dataset.weight_lbs = self.weight_entry.get_value()
                else:
                    self.dataset.weight = self.weight_entry.get_value()
                if parameters.config['preferences.use_bodyfat']:
                    bodyfat = self.bodyfat_entry.get_value()
                    if bodyfat > 0.1:
                        self.dataset.bodyfat = bodyfat
                    else:
                        self.dataset.bodyfat = None
                if parameters.config['preferences.use_note']:
                    note = self.note_buffer.get_text(
                            self.note_buffer.get_start_iter(),
                            self.note_buffer.get_end_iter()).strip()
                    if note != '':
                        self.dataset.note = note
                    else:
                        self.dataset.note = None
            except:
                title = _('Error: Wrong Format')
                message = _('The data entered is not in the correct format!')
                MessageDialog(
                        type_='error', title=title, message=message).run()
                return self.run()
            self.dialog.hide()
            return self.dataset
        else:
            self.dialog.hide()
            return None

    # callback methods
    def on_focus(self, entry, event):
        """Prevents a selection and puts the cursor at the end
        of the entry instead."""
        gobject.idle_add(entry.set_position, -1)

    def on_insert(self, entry, text, length, *args):
        """Prevents '+' and '-' from being inserted into the entry and
        triggers the appropriate callback function in stead."""
        if text in ['+', '-']:
            position = entry.get_position()
            entry.emit_stop_by_name('insert_text')
            # check first for use_calendar; date_entry might not exist
            if (not parameters.config['preferences.use_calendar']
                            and entry == self.date_entry):
                    gobject.idle_add(
                            self.date_key_press, entry, text, position)
            if entry == self.weight_entry:
                gobject.idle_add(self.weight_key_press, text)

    # helper methods

    def date_key_press(self, entry, text, position):
        """Tests, which key was pressed and increments/decrements the
        date in date entry by one day if possible."""
        try:
            date_ = util.str2date(entry.get_text())
        except ValueError:
            entry.handler_block(self.date_insert_signal)
            orig_text = entry.get_text()
            new_text = orig_text[:position] + text + orig_text[position:]
            entry.set_text(new_text)
            entry.set_position(position+1)
            entry.handler_unblock(self.date_insert_signal)
            return
        else:
            if text == '+':
                date_ += timedelta(days=1)
            elif text == '-':
                date_ -= timedelta(days=1)
            entry.handler_block(self.date_insert_signal)
            entry.set_text(str(date_))
            entry.set_position(-1)
            entry.handler_unblock(self.date_insert_signal)

    def weight_key_press(self, text):
        """Tests, which key was pressed and increments/decrements the
        value in the weight entry by 0.1 if possible."""
        if text == '+':
            self.weight_entry.spin(gtk.SPIN_STEP_FORWARD, increment=0.1)
        elif text == '-':
            self.weight_entry.spin(gtk.SPIN_STEP_BACKWARD, increment=0.1)
