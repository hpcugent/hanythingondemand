#!/usr/bin/env python
# #
# Copyright 2009-2015 Ghent University
#
# This file is part of hanythingondemand
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/hanythingondemand
#
# hanythingondemand is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# hanythingondemand is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hanythingondemand. If not, see <http://www.gnu.org/licenses/>.
# #
"""
Utility functions for printing text in tables.

@author: Ewan Higgs (Universiteit Gent)
"""

from itertools import chain

def _mk_fmt_str(fields):
    """Calculate the format string for printing the template parameters."""
    field_lens = []
    for field in fields:
        field_lens.append(max(map(len, field)))
    fmt_str = ""
    for i, field_len in enumerate(field_lens):
        fmt_str += '%%-%ds' % field_len
        if i != len(field_lens)-1:
            fmt_str += '\t'
    return fmt_str


def _pivot(rows):
    """Given a list of rows, pivot it into a list of columns - or vice versa."""
    if not rows:
        return []

    cols = []
    ncols = len(rows[0])
    for col in range(ncols):
        cols.append([row[col] for row in rows])
    return cols

def format_table(rows, headers=None):
    """
    Formats a table of data. 
    Params
    ------
    rows - list of lists containing each row of data
    headers - None or list of strings for the table header.

    The number of headers must be the same as the number of columns or None.
    """

    if not rows:
        raise ValueError('No rows to print')

    if headers is not None and len(headers) != len(rows[0]):
        raise ValueError('Headers and rows must have the same length')

    out = ''
    if headers:
        cols = _pivot([headers] + rows)
        fmt_str = _mk_fmt_str(cols)
        out = fmt_str % tuple(headers)
        out += '\n'
    else:
        cols = _pivot(rows)
        fmt_str = _mk_fmt_str(cols)

    for i, line in enumerate(rows):
        out += fmt_str % tuple(line)
        if i != len(rows)-1:
            out += '\n'
    return out
