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
Calculate Hadoop configuration parameters based on HortonWorks' recommendations
and my own testing.
HortonWorks recommendations are here:

http://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.0.6.0/bk_installing_manually_book/content/rpm-chap1-11.html

@author: Ewan Higgs (Ghent University)
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
    mem_dflts = memory_defaults(node_info)

    java_map_mem = format_memory(0.8 * mem_dflts.ram_per_container, round_val=True)
    java_reduce_mem = format_memory(0.8 * 2 * mem_dflts.ram_per_container, round_val=True)
    # In my tests, Yarn gets shirty if I try to run a job and these values are set to
    # more then 8g:
    map_memory = round_mb(mem_dflts.ram_per_container)
    reduce_memory = round_mb(2 * mem_dflts.ram_per_container)
    dflts = {
        'mapreduce.framework.name': 'yarn',
        'mapreduce.map.java.opts': '-Xmx%s' % java_map_mem,
        'mapreduce.map.memory.mb': map_memory,
        'mapreduce.reduce.java.opts': '-Xmx%s' % java_reduce_mem,
        'mapreduce.reduce.memory.mb': reduce_memory,
        # io.sort.mb can't be > 2047mb
        'mapreduce.task.io.sort.mb': min(int(0.4 * map_memory), 2047),
        'yarn.app.mapreduce.am.staging-dir': '$localworkdir/tmp/hadoop-yarn/staging',
    }
    return dflts

def yarn_site_xml_defaults(workdir, node_info):
    '''
    Default entries for the yarn-site.xml config file.
    '''
    mem_dflts = memory_defaults(node_info)
    ncores = node_info['cores']
    max_alloc = round_mb(mem_dflts.ram_per_container * mem_dflts.num_containers)
    min_alloc = round_mb(mem_dflts.ram_per_container)
    dflts = {
        'yarn.nodemanager.aux-services': 'mapreduce_shuffle',
        'yarn.scheduler.maximum-allocation-mb': max_alloc,
        'yarn.scheduler.minimum-allocation-mb': min_alloc,
        'yarn.nodemanager.resource.memory-mb': max_alloc,
        'yarn.nodemanager.vmem-check-enabled':'false',
        'yarn.nodemanager.vmem-pmem-ratio': 2.1,
        'yarn.nodemanager.hostname': '$dataname',
        'yarn.nodemanager.webapp.address': '$hostaddress:8042',
        'yarn.resourcemanager.hostname': '$masterdataname',
        'yarn.resourcemanager.webapp.address': '$masterhostaddress:8088',
        'yarn.resourcemanager.webapp.https.address': '$masterhostaddress:8090',
        'yarn.resourcemanager.scheduler.class': 'org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler',
        'yarn.scheduler.capacity.allocation.file': 'capacity-scheduler.xml',
        'yarn.scheduler.maximum-allocation-vcores': str(ncores),
        'yarn.scheduler.minimum-allocation-vcores': '1',
        'yarn.nodemanager.resource.cpu-vcores': str(ncores),
    }
    return dflts

def capacity_scheduler_xml_defaults(workdir, node_info):
    dflts = {
        'yarn.scheduler.capacity.root.queues': 'default',
        'yarn.scheduler.capacity.root.default.capacity': 100,
        'yarn.scheduler.capacity.root.default.minimum-user-limit-percent': 100,
        'yarn.scheduler.capacity.resource-calculator': 'org.apache.hadoop.yarn.util.resource.DominantResourceCalculator',
        'yarn.scheduler.capacity.root.default.acl_submit_applications': '$user',
        'yarn.scheduler.capacity.root.default.acl_administer_queue': '$user',
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
        'mapred-site.xml': mapred_site_xml_defaults,
        'yarn-site.xml': yarn_site_xml_defaults,
        'capacity-scheduler.xml': capacity_scheduler_xml_defaults,
    }
    config_dict = dict()
    for cfg, fn in cfg2fn.items():
        dflts = fn(workdir, node_info)
        config_dict[cfg] = dflts
    return config_dict
