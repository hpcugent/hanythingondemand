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

from collections import namedtuple
import os
import re

from hod.node.node import Node

def parse_memory(memstr):
    '''
    Given a string representation of memory, return the memory size in
    bytes. It supports up to terabytes.
    '''
    size = re.search(r'[bBkKmMgGtT]', memstr)
    if size is not None:
        coef = float(memstr[:size.start()])
        exp = memstr[size.start():size.end()]
    else:
        try:
            coef = float(memstr)
        except ValueError, e:
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
    raise RuntimeError('Unable to parse memory amount:', memstr)

def format_memory(mem, round_val=False):
    '''
    Given an integer 'mem', return the string with associated units Note
    that this is used to set heap sizes for the jvm awhich doesn't accept non
    integer sizes. Therefore this truncates.

    If round_val is set, then the value will be rounded to the nearest unit
    where mem will be over 1.

    Note also that this supports outputting 'b' for bytes and java -Xmx${somenum}b won't work.
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

# mapping for total system memory -> reserved for OS
# Retrieved from:
# http://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.0.6.0/bk_installing_manually_book/content/rpm-chap1-11.html
MemRec = namedtuple('MemRec', ['total','os'])
_RECOMMENDATIONS = [
    MemRec(parse_memory('8g'), parse_memory('2g')),
    MemRec(parse_memory('16g'), parse_memory('2g')),
    MemRec(parse_memory('24g'), parse_memory('4g')),
    MemRec(parse_memory('48g'), parse_memory('6g')),
    MemRec(parse_memory('64g'), parse_memory('8g')),
    MemRec(parse_memory('72g'), parse_memory('8g')),
    MemRec(parse_memory('96g'), parse_memory('12g')),
    MemRec(parse_memory('128g'), parse_memory('24g')),
    MemRec(parse_memory('256g'), parse_memory('32g')),
    MemRec(parse_memory('512g'), parse_memory('64g')),
]

def reserved_memory(totalmem):
    for mem in _RECOMMENDATIONS:
        if totalmem <= mem.total:
            return mem.os
    return _RECOMMENDATIONS[-1].os

def min_container_size(totalmem):
    if totalmem < parse_memory('4G'):
        return  256 * (1024**2)
    elif totalmem < parse_memory('8G'):
        return 512 * (1024**2)
    elif totalmem < parse_memory('24G'):
        return 1024**3
    else:
        return 2 * (1024**3)

MemDefaults = namedtuple('MemDefaults',
        [
            'available_memory',
            'min_container_sz',
            'num_containers',
            'ram_per_container'
        ])

def memory_defaults(total_memory, ncores):
    available_memory = total_memory - reserved_memory(total_memory)
    min_container_sz = min_container_size(total_memory)
    num_containers = min(2*ncores, total_memory/min_container_sz)
    ram_per_container = max(min_container_sz, total_memory/num_containers)
    return MemDefaults(
            available_memory,
            min_container_sz,
            num_containers,
            ram_per_container)

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

def core_site_xml_defaults(workdir, node_info, config_dict):
    '''
    Default entries for the core-site.xml config file.
    '''
    blocksize = os.statvfs(workdir).f_bsize

    dflts = {}
    dflts['fs.inmemory.size.mb'] = 200
    # If there is hdfs, probably don't set to this blocksize.
    dflts['io.file.buffer.size'] = blocksize
    dflts['io.sort.factor'] = 64
    dflts['io.sort.mb'] = 256
    return dflts

def mapred_site_xml_defaults(workdir, node_info, config_dict):
    '''
    Default entries for the mapred-site.xml config file.
    '''
    total_memory = int(node_info['memory']['meminfo']['memtotal'])
    ncores = len(node_info['usablecores'])
    mem_dflts = memory_defaults(total_memory, ncores)
    dflts = {}
    dflts['mapreduce.map.memory.mb'] = mem_dflts.ram_per_container
    dflts['mapreduce.reduce.memory.mb'] = 2 * mem_dflts.ram_per_container
    dflts['mapreduce.map.java.opts'] = '-Xmx%s' % format_memory(0.8 * mem_dflts.ram_per_container, round_val=True)
    dflts['mapreduce.reduce.java.opts'] = '-Xmx%s' % format_memory(0.8 * 2 * mem_dflts.ram_per_container, round_val=True)
    return dflts

def yarn_site_xml_defaults(workdir, node_info, config_dict):
    '''
    Default entries for the yarn-site.xml config file.
    '''
    total_memory = node_info['memory']['meminfo']['memtotal']
    ncores = len(node_info['usablecores'])
    mem_dflts = memory_defaults(total_memory, ncores)

    dflts = {}
    dflts['yarn.nodemanager.resource.memory-mb'] = mem_dflts.ram_per_container * mem_dflts.num_containers
    dflts['yarn.nodemanager.minimum-allocation-mb'] = mem_dflts.ram_per_container
    dflts['yarn.nodemanager.maximum-allocation-mb'] = mem_dflts.ram_per_container * mem_dflts.num_containers
    return dflts

def autogen_hadoop_config(workdir, config_dict):
    '''
    Bless a hadoop config with automatically generated information based on
    the nodes. i.e. memory settings and file system block size.
    '''
    node = Node()
    node_info = node.go()
    cfg2fn = {
            'core-site.xml': core_site_xml_defaults,
            'mapred-site.xml': mapred_site_xml_defaults,
            'yarn-site.xml': yarn_site_xml_defaults,
            }
    for cfg, fn in cfg2fn.items():
        dflts = fn(workdir, node_info, config_dict)
        if cfg not in config_dict:
            config_dict[cfg] = dflts
        else:
            update_defaults(config_dict[cfg], dflts)
    return config_dict
