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
IPython Notebook autoconfiguration.

@author: Ewan Higgs (Ghent University)
"""

import hod.config.autogen.hadoop as hcah
import hod.config.autogen.common as hcac
import tempfile


def spark_defaults(_, node_info):
    '''
    Generate spark defaults so spark uses all the resources that yarn is able to
    provide.

    Defaults here are based on Cloudera's recommendations here: 
    http://blog.cloudera.com/blog/2015/03/how-to-tune-your-apache-spark-jobs-part-2/

    We use 2 cores per executor based on discussion found here:
    http://stackoverflow.com/questions/24622108/apache-spark-the-number-of-cores-vs-the-number-of-executors
    '''
    memory_defaults = hcah.memory_defaults(node_info)
    num_nodes = node_info['num_nodes']
    cores_per_executor = min(2, node_info['cores'])
    instances_per_node = node_info['cores'] / cores_per_executor
    # -1 because we want one less executor instance on the application master
    # If we have only one node then we don't expect the driver to be very busy, so
    # we can give the executors more memory.
    instances = max((num_nodes * instances_per_node) - 1, 1)
    memory = hcac.round_mb(memory_defaults.available_memory / instances_per_node)
    dflts = {
        'spark.executor.cores': cores_per_executor,
        'spark.executor.instances': instances,
        'spark.executor.memory':  str(memory) + 'M',
        'spark.local.dir': tempfile.gettempdir(),
    }
    return dflts

def autogen_config(workdir, node_info):
    '''
    Bless an ipython notebook config with automatically generated information
    based on the nodes.

    NB: The name is important here; it must be 'autogen_config' as it's loaded
    lazily from hod.config.config.
    '''
    cfg2fn = {
    }
    cfg2fn = {
        # Pulled in from Hadoop
        'capacity-scheduler.xml': hcah.capacity_scheduler_xml_defaults,
        'core-site.xml': hcah.core_site_xml_defaults,
        'mapred-site.xml': hcah.mapred_site_xml_defaults,
        'yarn-site.xml': hcah.yarn_site_xml_defaults,
        # Spark/IPython notebook specific
        'spark-defaults.conf': spark_defaults,
    }
    config_dict = dict()
    for cfg, fn in cfg2fn.items():
        dflts = fn(workdir, node_info)
        config_dict[cfg] = dflts
    return config_dict
