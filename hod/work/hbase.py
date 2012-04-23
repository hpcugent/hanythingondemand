
#
# Copyright 2012 Stijn De Weirdt
# 
# This file is part of HanythingOnDemand,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
from hod.work.work import Work
from hod.work.hadoop import Hadoop
from hod.config.hbase import HbaseOpts

from hod.config.customtypes import HostnamePort, Directories, Servers
from hod.commands.hadoop import HbaseZooKeeper, HbaseMaster, HbaseRegionServer

from vsc import fancylogger


import os, copy

class Hbase(HbaseOpts, Hadoop):
    """Base Hbase work class"""
    def __init__(self, ranks, shared):
        Work.__init__(self, ranks) ## don't use Hadoop.__init__, better to redo Hadoop.__init__ with work + opts
        HbaseOpts.__init__(self, shared)

    def set_service_defaults(self, mis):
        """Set service specific default"""
        self.log.debug("Setting servicedefaults for %s" % mis)
        if mis in ('hbase.rootdir',):
            ## use the fs.default.name with additional path
            rootdir = copy.deepcopy(self.params['fs.default.name'])
            rootdir.fspath = '/hbase'
            self.log.debug("Set mis %s to %s" % (mis, rootdir))
            self.params[mis] = rootdir
        elif mis.startswith('hbase.') and mis.endswith('dns.interface'):
            ## use the interface name that can reach the namenode
            intf = self.interface_to_nn()
            self.log.debug("Set mis %s to interface %s (%s)" % (mis, intf[2], intf))
            self.params[mis] = intf[2]
        elif mis in ('hbase.zookeeper.quorum',):
            ## add master as quorum node
            nn_idx = self.thisnode.network.index(self.interface_to_nn())
            master_intf = self.allnodes[self.masterrank]['network'][nn_idx]
            svs = Servers(master_intf[0])
            self.log.debug("Set mis %s for masterrank %s and interface_index_to_nn %s to %s" % (mis, self.masterrank, nn_idx, svs))
            self.params[mis] = svs
        elif mis in ('hbase.zookeeper.property.dataDir', 'hbase.tmp.dir',):
            ## set directories relative to basedir
            tmpdir = os.path.join(self.basedir, mis)
            self.log.debug("%s not set. using  %s" % (mis, tmpdir))
            self.params[mis] = Directories(tmpdir)
        elif mis in ('HBASE_CONF_DIR', 'HBASE_PID_DIR', 'HBASE_LOG_DIR',):
            ## use the HADOOP versions
            hadoopname = mis.replace('HBASE_', 'HADOOP_')
            hadoopval = self.env_params.get(hadoopname, None)
            self.log.debug("Setting mis %s by using hadoop variable %s with value %s" % (mis, hadoopname, hadoopval))
            self.env_params[mis] = hadoopval
        elif mis in ('HBASE_HEAPSIZE',):
            ## use half memory (in MB)
            mem = (self.thisnode.memory['meminfo']['memfree'] + self.thisnode.memory['meminfo']['cached']) / (2 * 1024 * 1024)
            self.log.debug("Setting mis %s to half available memory %s MB" % (mis, mem))
            self.env_params[mis] = mem
        else:
            self.log.warn("Variable %s not found in service defaults" % mis) ## TODO is warn enough?
            return True ## not_mis_found

    def start_work_service_master(self):
        """Start service on master"""
        self.set_niceness(4, 2, 3, 'socket:0', varname='HBASE_NICENESS') ## same as mapred jobtracker

        self.log.info("Start zookeeper service on master.")
        command = HbaseZooKeeper(self.daemon_script, start=True)
        command.run()
        self.log.info("Start hbase master service on master.")
        command = HbaseMaster(self.daemon_script, start=True)
        command.run()


    def start_work_service_slaves(self):
        """Run start_service on slaves"""
        self.set_niceness(15, 2, 7, varname='HBASE_NICENESS') ## same as mapred tasktracker
        self.log.info("Start regionserver service on slaves.")
        command = HbaseRegionServer(self.daemon_script, start=True)
        command.run()

    def stop_work_service_master(self):
        """Stop service on master"""
        self.log.error("Stop hbase master service on master.")
        command = HbaseMaster(self.daemon_script, start=False)
        command.run()
        self.log.info("Stop zookeeper service on master.")
        command = HbaseZooKeeper(self.daemon_script, start=False)
        command.run()


    def stop_work_service_slaves(self):
        """Run stop_service on slaves"""
        self.log.info("Stop regionserver service on slaves.")
        command = HbaseRegionServer(self.daemon_script, start=False)
        command.run()

