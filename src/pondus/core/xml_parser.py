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

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

from pondus import parameters
from pondus.core import util
from pondus.core.dataset import Dataset

class DatasetHandler(ContentHandler):
    """Defines how to parse the xml-file."""
    def __init__(self):
        self.datasets = {}
    def startElement(self, name, attr):
        self.current_tag = name
        if name == parameters.datasettag:
            self.id_data = int(attr.getValue(attr.getNames()[0]).encode('utf-8'))
    def endElement(self, name):
        if name == parameters.datasettag:
            self.datasets[self.id_data] = Dataset(
                                            self.id_data,
                                            util.str2date(self.date),
                                            float(self.weight))
    def characters(self, content):
        if self.current_tag == parameters.datetag:
            self.date = content
        if self.current_tag == parameters.weighttag:
            self.weight = content


def read(filepath):
    """Parses the xml-file in filepath and return an AllDatasets
    object."""
    util.check_filepath(filepath)
    parser = make_parser()
    handler = DatasetHandler()
    parser.setContentHandler(handler)
    parser.parse(filepath)
    return handler.datasets

def write(dataset_iter, filepath):
    """Writes the datasets to the file in filepath."""
    dom = util.create_xml_base()
    for dataset in dataset_iter:
        dataset.write_to_dom(dom)
    util.dom2file(dom, filepath)
