##
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
##
"""
@author: Martijn Oldenhof (KU Leuven)
"""

from collections import namedtuple
from hod.config.autogen.common import (blocksize,
        available_memory, parse_memory, format_memory, round_mb)

__all__ = ['autogen_config']

MemDefaults = namedtuple('MemDefaults', [
    'available_memory',
    'min_container_sz',
    'num_containers',
    'ram_per_container'
])

def min_container_size(totalmem):
    '''
    Given an amount of memory in bytes, return the amount of memory that
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

def memory_defaults(node_info):
    '''
    Return default memory information.
    '''
    ncores = node_info['cores']
    hadoop_memory = available_memory(node_info)
    min_container_sz = min_container_size(hadoop_memory)
    num_containers = min(2*ncores, hadoop_memory/min_container_sz)
    ram_per_container = max(min_container_sz, hadoop_memory/num_containers)
    return MemDefaults(
            hadoop_memory,
            min_container_sz,
            num_containers,
            ram_per_container)

def core_site_xml_defaults(workdir, node_info):
    '''
    Default entries for the core-site.xml config file.
    '''

    dflts = {
        'dfs.replication': 1,
        'fs.defaultFS': 'hdfs://$masterhostaddress:54310',
        'fs.inmemory.size.mb': 200,
        'hadoop.rpc.socket.factory.class.default': 'org.apache.hadoop.net.StandardSocketFactory',
        'hadoop.tmp.dir': '$localworkdir',
        # If there is hdfs, probably don't set to this blocksize.
        'io.file.buffer.size': blocksize(workdir),
        'io.sort.factor': 64,
        'io.sort.mb': 256,
    }
    return dflts

def hdfs_site_xml_defaults(workdir, node_info):
    '''
    Default entries for the hdfs-site.xml config file.
    '''

    dflts = {
        'dfs.namenode.name.dir': '$localworkdir/dfs/name',
        'dfs.datanode.data.dir': '$localworkdir/dfs/data',
    }
    return dflts

def hbase_site_xml_defaults(workdir, node_info):
    '''
    Default entries for the hbase-site.xml config file.
    '''

    dflts = {
        'hbase.cluster.distributed': 'true',
        'hbase.rootdir': 'hdfs://$masterhostaddress:54310/hbase',
        'hbase.zookeeper.quorum': '$masterhostaddress',
        'hbase.zookeeper.property.dataDir': '$localworkdir/zookeeper',
        'hbase.regionserver.info.port.auto': 'true',
        'hbase.regionserver.port': '17020',
    }
    return dflts

def masters_defaults(workdir, node_info):
    '''
    Default entries for the masters config file.
    '''

    dflts = {
        '': '$masterhostaddress',
    }
    return dflts


def autogen_config(workdir, node_info):
    '''
    Bless a hadoop config with automatically generated information based on
    the nodes. i.e. memory settings and file system block size.

    NB: The name is important here; it must be 'autogen_config' as it's loaded
    lazily from hod.config.config.

    '''
    cfg2fn = {
        'core-site.xml': core_site_xml_defaults,
        'hdfs-site.xml': hdfs_site_xml_defaults,
        'masters': masters_defaults,
        'hbase-site.xml': hbase_site_xml_defaults,
    }
    config_dict = dict()
    for cfg, fn in cfg2fn.items():
        dflts = fn(workdir, node_info)
        config_dict[cfg] = dflts
    return config_dict
