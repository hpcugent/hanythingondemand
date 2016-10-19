#!/usr/bin/env python
# #
# Copyright 2009-2016 Ghent University
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

def _mk_fmt_str(fields):
    """Calculate the format string for printing the template parameters."""
    field_lens = [max(map(len, field)) for field in fields]
    fmt_str = '\t'.join(['%%-%ds' % field_len for field_len in field_lens])
    return fmt_str


def _pivot(rows):
    """Given a list of rows, pivot it into a list of columns - or vice versa."""
    if not rows:
        return []

    ncols = len(rows[0])
    cols = [[row[col] for row in rows] for col in range(ncols)]
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

    if len(set(map(len, rows))) != 1:
        raise ValueError('Not all of the rows have the same length')

    out = ''
    if headers:
        cols = _pivot([headers] + rows)
        fmt_str = _mk_fmt_str(cols)
        out = fmt_str % tuple(headers) + '\n'
    else:
        cols = _pivot(rows)
        fmt_str = _mk_fmt_str(cols)

    out += '\n'.join([fmt_str % tuple(line) for line in rows])
    return out
