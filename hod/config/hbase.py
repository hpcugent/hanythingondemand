"""
HDFS config and options
"""

from hod.config.customtypes import Servers, HdfsFs, ParamsDescr, Boolean

from hod.config.hadoopopts import HadoopOpts
from hod.config.hadoopcfg import HadoopCfg
from hod.commands.hadoop import HbaseVersion

import re, os

## namenode is set in core
HBASE_OPTS = ParamsDescr({
    'hbase.rootdir': [HdfsFs(), 'FINAL The directory shared by RegionServers (eg hdfs://namenode.example.org:8020/hbase)'],
    'hbase.cluster.distributed': [Boolean(True), 'FINAL The mode the cluster will be in. Possible values are  false: standalone and pseudo - distributed setups with managed Zookeeper' +
                                      ' true: fully - distributed with unmanaged Zookeeper Quorum (see hbase - env.sh)'],
    'hbase.zookeeper.property.clientPort':[2222, 'Property from ZooKeepers config zoo.cfg. The port at which the clients will connect.'],
    'hbase.zookeeper.quorum':[Servers(), 'Comma separated list of servers in the ZooKeeper Quorum. For example, "host1.mydomain.com,host2.mydomain.com,host3.mydomain.com".' +
                                        'By default this is set to localhost for local and pseudo-distributed modes of operation. For a fully-distributed setup, this should be set to a full ' +
                                        ' list of ZooKeeper quorum servers. If HBASE_MANAGES_ZK is set in hbase-env.sh this is the list of servers which we will start/stop ZooKeeper on.'],
    'hbase.zookeeper.property.dataDir':[None, 'Property from ZooKeepers config zoo.cfg. The directory where the snapshot is stored.'],
    'hbase.tmp.dir':[None, "Temporary directory on the local filesystem. Change this setting to point to a location more permanent than '/tmp' (The '/tmp' directory is often cleared on machine restart)."],

    'hbase.zookeeper.dns.interface':[None, 'The name of the Network Interface from which a ZooKeeper server should report its IP address.'],
    'hbase.regionserver.dns.interface':[None, 'The name of the Network Interface from which a region server should report its IP address.'],
    'hbase.master.dns.interface': [None, 'The name of the Network Interface from which a master should report its IP address.'],

    'hbase.client.scanner.caching':[100, 'Default 1 is too low'],

    ## 'mapred.mapred.child.java.opts':[,'']
})

HBASE_SECURITY_SERVICE = ParamsDescr({
})

HBASE_ENV_OPTS = ParamsDescr({
    'HBASE_CONF_DIR': [None, 'The directory where the config files are located. Default is HBASE_HOME/conf.'],
    'HBASE_LOG_DIR': [None, 'The directory where the daemons log files are stored. They are automatically created if they dont exist.'],
    'HBASE_PID_DIR': [None, 'The directory where the daemons pid files are stored. They are automatically created if they dont exist.'],

    'HBASE_MANAGE_ZK':[Boolean(True), 'Use HBase ZooKeeper (true) or external one (false)'],
    'HBASE_HEAPSIZE':[None, 'HBase heapsize'],
})

class HbaseCfg(HadoopCfg):
    """Hbase cfg"""
    def __init__(self):
        HadoopCfg.__init__(self)
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
        self.which_hbase()
        self.hbase_version()

        ## add the habse required jars
        import glob
        self.hbase_jars += glob.glob("%s/hbase*jar" % self.hbasehome)
        self.hbase_jars += glob.glob("%s/conf")
        self.hbase_jars += glob.glob("%s/lib/zookeeper*jar" % self.hbasehome)

        ## add paths to look for hbase daemon scripts
        self.extrasearchpaths.append(os.path.join(self.hbasehome, 'bin'))
        self.extrasearchpaths.append(os.path.join(self.hbasehome, 'sbin'))
        self.log.debug("hbase extrasearchpaths %s" % self.extrasearchpaths)

    def which_hbase(self):
        """Locate HBASE_HOME and hadoop"""
        self.hbase = self.which_exe('hbase')
        self.hbasehome = self.which_exe('hbase', stripbin=True)

    def hbase_version(self):
        """Set the major and minor hadoopversion"""
        hv = HbaseVersion() ## not i all versions?
        hv_out, hv_err = hv.run()

        hbaseVerRegExp = re.compile("^\s*Hadoop\s+(\d+)\.(\d+)(?:\.(\d+)(?:(?:-|_)(\S+))?)?\s*$", re.M)
        verMatch = hbaseVerRegExp.search(hv_out)
        if verMatch:
            self.hbaseversion['major'] = int(verMatch.group(1))
            self.hbaseversion['minor'] = int(verMatch.group(2))
            if verMatch.group(3):
                self.hbaseversion['small'] = int(verMatch.group(3))
            if verMatch.group(4):
                self.hbaseversion['suffix'] = verMatch.group(4)
            self.log.debug('Version found from hbase command: %s' % self.hbaseversion)
        else:
            self.log.error("No HBase hbaseversion found (output %s err %s)" % (hv_out, hv_err))



class HbaseOpts(HbaseCfg, HadoopOpts):
    """Hbase options"""
    def __init__(self, shared=None, basedir=None):
        HadoopOpts.__init__(self, shared=shared, basedir=basedir)
        HbaseCfg.__init__(self)

        self.attrs_to_share += ['hbase', 'hbasehome', 'hbase_jars']

    def init_defaults(self):
        """Create the default list of params and description"""
        self.log.debug("Adding init defaults.")
        self.add_from_opts_dict(HBASE_OPTS)

        self.log.debug("Adding init env_params. Adding HBASE_ENV_OPTS %s" % HBASE_ENV_OPTS)
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
        self.setenv(varname, varvalue)
