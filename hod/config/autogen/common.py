##
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
##
"""
Nothing here for now.

@author: Ewan Higgs (Ghent University)
"""

from os.path import dirname
import errno
import os
import re

def blocksize(path):
    '''
    Find the block size for the file system given a path. If the path points to
    a directory that does not yet exist, use the parent directory under the
    assumption that the provided path will appear later on the existing file
    system (as opposed to being a new mount).
    '''
    try:
        return os.statvfs(path).f_bsize
    except OSError, e:
        if e.errno == errno.ENOENT:
            return os.statvfs(dirname(path)).f_bsize
        raise

def set_default(d, key, val):
    '''If a value is not in dict d, set it'''
    if key not in d:
        d[key] = val
    return d

def update_defaults(d1, d2):
    '''Update dict d1 with data from d2 iff values are not already in d1.'''
    for k, v in d2.items():
        set_default(d1, k, v)
    return d1

def parse_memory(memstr):
    '''
    Given a string representation of memory, return the memory size in
    bytes. It supports up to terabytes.

    No size defaults to byte:

    >>> parse_memory('200')
    200

    Also supports k for kilobytes:

    >>> parse_memory('200k')
    204800


    kb, mb, gb, tb, etc also works:

    >>> parse_memory('200kb')
    204800
    '''
    size = re.search(r'[bBkKmMgGtT]', memstr)
    if size is not None:
        coef = float(memstr[:size.start()])
        exp = memstr[size.start():size.end()]
    else:
        try:
            coef = float(memstr)
        except ValueError:
            raise RuntimeError('Unable to parse memory string:', memstr)
        exp = ''

    if exp in ['', 'b', 'B']:
        return coef
    elif exp in ['k', 'K']:
        return coef * 1024
    elif exp in ['m', 'M']:
        return coef * (1024 ** 2)
    elif exp in ['g', 'G']:
        return coef * (1024 ** 3)
    elif exp in ['t', 'T']:
        return coef * (1024 ** 4)
    # Should not be able to get here
    raise RuntimeError('Unable to parse memory amount:', memstr) # pragma: no cover

def format_memory(mem, round_val=False):
    '''
    Given an integer 'mem' for the amount of memory in bytes, return the string
    with associated units. If round_val is set, then the value will be rounded
    to the nearest unit where mem will be over 1.

    Note that this is used to set heap sizes for the jvm which doesn't accept
    non integer sizes. Therefore this truncates.

    Note also that this supports outputting 'b' for bytes even though java
    -Xmx${somenum}b won't work.
    '''
    units = 'bkmgt'
    unit_idx = len(units) - 1
    while unit_idx > 0:
        mem_in_units = mem/(1024.**unit_idx)
        if mem >= (1024**unit_idx):
            if round_val:
                return '%d%s' % (round(mem_in_units), units[unit_idx])
            elif mem_in_units - int(mem_in_units) == 0:
                return '%d%s' % (mem_in_units, units[unit_idx])
        unit_idx -= 1
    return '%db' % mem
