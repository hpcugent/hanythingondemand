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
Nothing here for now.

@author: Ewan Higgs (Ghent University)
"""
import hod.config.autogen.hadoop as hcah

__all__ = ['autogen_config']

def core_site_xml_defaults(workdir, node_info):
    dflts = {
        'hadoop.tmp.dir': '$workdir/tmp'
    }
    base_hadoop_dflts = hcah.core_site_xml_defaults(workdir, node_info)
    base_hadoop_dflts.update(dflts)
    return base_hadoop_dflts

def mapred_site_xml_defaults(workdir, node_info):
    dflts = {
        'lustre.dir': '$workdir',
        # hadoop.ln.cmd this is mentioned in the docs but all uses are commented
        # out.
        'hadoop.ln.cmd': '/bin/ln',
    }
    base_hadoop_dflts = hcah.mapred_site_xml_defaults(workdir, node_info)
    base_hadoop_dflts.update(dflts)
    return base_hadoop_dflts

def yarn_site_xml_defaults(workdir, node_info):
    dflts = {
        # Hadoop-on-lustre2 wants to find dirs with
        # $workdir/$(nodemanager-hostname) which in our case is 'dataname'
        'yarn.nodemanager.local-dirs': '$workdir/$dataname',
    }
    base_hadoop_dflts = hcah.yarn_site_xml_defaults(workdir, node_info)
    base_hadoop_dflts.update(dflts)
    return base_hadoop_dflts

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
        'capacity-scheduler.xml': hcah.capacity_scheduler_xml_defaults,
    }
    config_dict = dict()
    for cfg, fn in cfg2fn.items():
        dflts = fn(workdir, node_info)
        config_dict[cfg] = dflts
    return config_dict
