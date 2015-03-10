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
from hod.node.node import Node
from hod.config.autogen.common import (blocksize,
        parse_memory, format_memory)

__all__ = ['autogen_config']

# mapping for total system memory -> reserved for OS
# Retrieved from:
# http://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.0.6.0/bk_installing_manually_book/content/rpm-chap1-11.html
MemRec = namedtuple('MemRec', ['total', 'os'])
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

MemDefaults = namedtuple('MemDefaults', [
    'available_memory',
    'min_container_sz',
    'num_containers',
    'ram_per_container'
])

def reserved_memory(totalmem):
    '''
    Given an amount of memory in bytes, return the amount of memory that
    should be reserved by the operating system (also in bytes).
    '''
    for mem in _RECOMMENDATIONS:
        if totalmem <= mem.total:
            return mem.os
    # totalmem > 512g
    return _RECOMMENDATIONS[-1].os

def min_container_size(totalmem):
    '''
    Given an amount of memory in bytes, return theh amount of memory that
    represents the minimum amount of memory (in bytes) to be allocated in a Yarn
    container.
    '''
    if totalmem < parse_memory('4G'):
        return  256 * (1024**2)
    elif totalmem < parse_memory('8G'):
        return 512 * (1024**2)
    elif totalmem < parse_memory('24G'):
        return 1024**3
    else:
        return 2 * (1024**3)

def memory_defaults(total_memory, ncores):
    '''
    Return default memory information.
    '''
    available_memory = total_memory - reserved_memory(total_memory)
    min_container_sz = min_container_size(total_memory)
    num_containers = min(2*ncores, total_memory/min_container_sz)
    ram_per_container = max(min_container_sz, total_memory/num_containers)
    return MemDefaults(
            available_memory,
            min_container_sz,
            num_containers,
            ram_per_container)

def core_site_xml_defaults(workdir, node_info):
    '''
    Default entries for the core-site.xml config file.
    '''

    dflts = {
        'dfs.replication': 1,
        'fs.defaultFS': 'file:///',
        'fs.inmemory.size.mb': 200,
        'hadoop.rpc.socket.factory.class.default': 'org.apache.hadoop.net.StandardSocketFactory',
        'hadoop.tmp.dir': '$localworkdir',
        # If there is hdfs, probably don't set to this blocksize.
        'io.file.buffer.size': blocksize(workdir),
        'io.sort.factor': 64,
        'io.sort.mb': 256,
    }
    return dflts

def mapred_site_xml_defaults(workdir, node_info):
    '''
    Default entries for the mapred-site.xml config file.
    '''
    total_memory = int(node_info['memory']['meminfo']['memtotal'])
    ncores = len(node_info['usablecores'])
    mem_dflts = memory_defaults(total_memory, ncores)

    java_map_mem = format_memory(0.8 * mem_dflts.ram_per_container, round_val=True)
    java_reduce_mem = format_memory(0.8 * 2 * mem_dflts.ram_per_container, round_val=True)

    dflts = {
        'mapreduce.framework.name': 'yarn',
        'mapreduce.map.java.opts': '-Xmx%s' % java_map_mem,
        'mapreduce.map.memory.mb': mem_dflts.ram_per_container / (1024**2),
        'mapreduce.reduce.java.opts': '-Xmx%s' % java_reduce_mem,
        'mapreduce.reduce.memory.mb': 2 * mem_dflts.ram_per_container / (1024**2),
        'yarn.app.mapreduce.am.staging-dir': '$localworkdir/tmp/hadoop-yarn/staging',
    }
    return dflts

def yarn_site_xml_defaults(workdir, node_info):
    '''
    Default entries for the yarn-site.xml config file.
    '''
    total_memory = node_info['memory']['meminfo']['memtotal']
    ncores = len(node_info['usablecores'])
    mem_dflts = memory_defaults(total_memory, ncores)

    max_alloc = mem_dflts.ram_per_container * mem_dflts.num_containers / (1024**2)
    min_alloc = mem_dflts.ram_per_container / (1024**2)
    dflts = {
        'yarn.nodemanager.aux-services': 'mapreduce_shuffle',
        'yarn.nodemanager.maximum-allocation-mb': max_alloc,
        'yarn.nodemanager.minimum-allocation-mb': min_alloc,
        'yarn.nodemanager.resource.memory-mb': max_alloc,
        'yarn.nodemanager.vmem-check-enabled':'false',
        'yarn.nodemanager.vmem-pmem-ratio': 2.1,
        'yarn.resourcemanager.hostname': '$masterdataname',
        'yarn.resourcemanager.scheduler.class':'org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler',
        'yarn.scheduler.capacity.allocation.file': 'capacity-scheduler.xml',
    }
    return dflts

def capacity_scheduler_xml_defaults(workdir, node_info):
    dflts = {
        'yarn.scheduler.capacity.root.queues': 'default',
        'yarn.scheduler.capacity.root.default.capacity': 100,
        'yarn.scheduler.capacity.root.default.minimum-user-limit-percent': 100,
    }
    return dflts

def autogen_config(workdir):
    '''
    Bless a hadoop config with automatically generated information based on
    the nodes. i.e. memory settings and file system block size.

    NB: The name is important here; it must be 'autogen_config' as it's loaded
    lazily from hod.config.config.

    '''
    node = Node()
    node_info = node.go()
    cfg2fn = {
        'core-site.xml': core_site_xml_defaults,
        'mapred-site.xml': mapred_site_xml_defaults,
        'yarn-site.xml': yarn_site_xml_defaults,
        'capacity-scheduler.xml': capacity_scheduler_xml_defaults,
    }
    config_dict = dict()
    for cfg, fn in cfg2fn.items():
        dflts = fn(workdir, node_info)
        config_dict[cfg] = dflts
    return config_dict
