# #
# Copyright 2009-2013 Ghent University
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
#
"""
HDFS config and options

@author: Stijn De Weirdt
"""

import re
import os
import glob

from hod.config.customtypes import Servers, HdfsFs, ParamsDescr, Boolean
from hod.config.hadoopopts import HadoopOpts, Option
from hod.config.hadoopcfg import HadoopCfg, which_exe
from hod.commands.hadoop import HbaseVersion

from vsc.utils import fancylogger

_log = fancylogger.getLogger(fname=False)

# # namenode is set in core
HBASE_OPTS = ParamsDescr({
    'hbase.rootdir': Option(
        HdfsFs, None,
        'FINAL The directory shared by RegionServers (eg hdfs://namenode.example.org:8020/hbase)',
    ),
    'hbase.cluster.distributed': Option(
        Boolean, True,
        'FINAL The mode the cluster will be in. Possible values are  false: standalone and pseudo - distributed setups'
        'with managed Zookeeper true: fully - distributed with unmanaged Zookeeper Quorum (see hbase - env.sh)'
    ),
    'hbase.zookeeper.property.clientPort': Option(
        str, 2222,
        'Property from ZooKeepers config zoo.cfg. The port at which the clients will connect.',
    ),
    'hbase.zookeeper.quorum': Option(
        Servers, None,
        'Comma separated list of servers in the ZooKeeper Quorum. For example,'
        ' "host1.mydomain.com,host2.mydomain.com,host3.mydomain.com".By default this is set to localhost for local and'
        ' pseudo-distributed modes of operation. For a fully-distributed setup, this should be set to a full list of'
        ' ZooKeeper quorum servers. If HBASE_MANAGES_ZK is set in hbase-env.sh this is the list of servers which we will'
        ' start/stop ZooKeeper on.',
    ),
    'hbase.zookeeper.property.dataDir': Option(
        str, None,
        'Property from ZooKeepers config zoo.cfg. The directory where the snapshot is stored.',
    ),
    'hbase.tmp.dir': Option(
        str, None,
        "Temporary directory on the local filesystem. Change this setting to point to a location more permanent than"
        " '/tmp' (The '/tmp' directory is often cleared on machine restart).",
    ),

    'hbase.zookeeper.dns.interface': Option(
        str, None,
        'The name of the Network Interface from which a ZooKeeper server should report its IP address.',
    ),
    'hbase.regionserver.dns.interface': Option(
        str, None,
        'The name of the Network Interface from which a region server should report its IP address.',
    ),
    'hbase.master.dns.interface': Option(
        str, None,
        'The name of the Network Interface from which a master should report its IP address.',
    ),

    'hbase.client.scanner.caching': Option(str, '100', 'Default 1 is too low'),

    # # 'mapred.mapred.child.java.opts':[,'']
})

HBASE_SECURITY_SERVICE = ParamsDescr({
})

HBASE_ENV_OPTS = ParamsDescr({
    'HBASE_CONF_DIR': Option(str, None, 'The directory where the config files are located. Default is HBASE_HOME/conf.'),
    'HBASE_LOG_DIR': Option(str, None, 'The directory where the daemons log files are stored. They are automatically created if they dont exist.'),
    'HBASE_PID_DIR': Option(str, None, 'The directory where the daemons pid files are stored. They are automatically created if they dont exist.'),

    'HBASE_MANAGE_ZK': Option(Boolean, True, 'Use HBase ZooKeeper (true) or external one (false)'),
    'HBASE_HEAPSIZE': Option(str, None, 'HBase heapsize'),
})

def _which_hbase():
    """Locate HBASE_HOME and hadoop"""
    hbase = which_exe('hbase')
    hbasehome = which_exe('hbase', stripbin=True)
    return hbase, hbasehome

def _hbase_version():
    """Set the major and minor hadoopversion"""
    hv = HbaseVersion()  # not i all versions?
    hv_out, hv_err = hv.run()

    hbaseVerRegExp = re.compile("^\s*Hadoop\s+(\d+)\.(\d+)(?:\.(\d+)(?:(?:-|_)(\S+))?)?\s*$", re.M)
    verMatch = hbaseVerRegExp.search(hv_out)
    hbaseversion = {}
    if verMatch:
        hbaseversion['major'] = int(verMatch.group(1))
        hbaseversion['minor'] = int(verMatch.group(2))
        if verMatch.group(3):
            hbaseversion['small'] = int(verMatch.group(3))
        if verMatch.group(4):
            hbaseversion['suffix'] = verMatch.group(4)
        _log.debug(
            'Version found from hbase command: %s' % hbaseversion)
    else:
        _log.error("No HBase hbaseversion found (output %s err %s)" %
                       (hv_out, hv_err))
    return hbaseversion



class HbaseOpts(HadoopOpts):
    """Hbase options"""
    def __init__(self, shared=None, basedir=None):
        HadoopOpts.__init__(self, shared=shared, basedir=basedir)
        self.name = 'hbase'
        self.daemonname = 'hbase'

        self.hbasehome = None
        self.hbase = None
        self.hbaseversion = {'major':-1,
                             'minor':-1,
                             'suffix': None,
                             }
        self.hbase_jars = []

    def basic_cfg_extra(self):
        self.log.debug("Setting hbase location and version")
        self.hbase, self.hbasehome = _which_hbase()
        self.hbaseversion = _hbase_version()

        # # add the habse required jars
        self.hbase_jars += glob.glob("%s/hbase*jar" % self.hbasehome)
        self.hbase_jars += glob.glob("%s/conf")
        self.hbase_jars += glob.glob("%s/lib/zookeeper*jar" % self.hbasehome)

        # # add paths to look for hbase daemon scripts
        self.extrasearchpaths.append(os.path.join(self.hbasehome, 'bin'))
        self.extrasearchpaths.append(os.path.join(self.hbasehome, 'sbin'))
        self.log.debug("hbase extrasearchpaths %s" % self.extrasearchpaths)



        self.attrs_to_share += ['hbase', 'hbasehome', 'hbase_jars']

    def init_defaults(self):
        """Create the default list of params and description"""
        self.log.debug("Adding init defaults.")
        self.add_from_opts_dict(HBASE_OPTS)

        self.log.debug("Adding init env_params. Adding HBASE_ENV_OPTS %s" %
                       HBASE_ENV_OPTS)
        self.add_from_opts_dict(HBASE_ENV_OPTS, update_env=True)

    def init_security_defaults(self):
        """Add security options"""
        self.log.debug("Add HDFS security settings")
        self.add_from_opts_dict(HBASE_SECURITY_SERVICE)

    def pre_run_any_service(self):
        """To be run before any service start/wait/stop"""
        HadoopOpts.pre_run_any_service(self)

        varname = 'HBASE_CONF_DIR'
        varvalue = self.confdir
        self.log.debug("set %s in environment to %s" % (varname, varvalue))
        os.putenv(varname, varvalue)
