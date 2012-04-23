
#
# Copyright 2012 Stijn De Weirdt
# 
# This file is part of HanythingOnDemand,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
from hod.work.work import Work
from hod.work.hadoop import Hadoop
from hod.config.hdfs import HdfsOpts

from hod.config.customtypes import HostnamePort, Directories
from hod.commands.hadoop import NameNode, DataNode, FormatHdfs

from vsc import fancylogger


import os

class Hdfs(HdfsOpts, Hadoop):
    """Base Hdfs work class"""
    def __init__(self, ranks, shared):
        Work.__init__(self, ranks) ## don't use Hadoop.__init__, better to redo Hadoop.__init__ with work + opts
        HdfsOpts.__init__(self, shared)

    def set_service_defaults(self, mis):
        """Set service specific default"""
        self.log.debug("Setting servicedefaults for %s" % mis)
        if mis in ('dfs.name.dir', 'dfs.data.dir',):
            tmpdir = os.path.join(self.basedir, mis)
            self.log.debug("%s not set. using  %s" % (mis, tmpdir))
            self.params[mis] = Directories(tmpdir)
        elif mis in ('dfs.datanode.address',):
            intf = self.interface_to_nn()
            if intf:
                val = HostnamePort('%s:50090' % intf[0])
                self.params[mis] = val
                self.log.debug("%s not set. using  %s" % (mis, val))
            else:
                self.log.warn("could not set %s. no intf found for namenode")
        elif mis in ('dfs.datanode.ipc.address',):
            intf = self.interface_to_nn()
            if intf:
                val = HostnamePort('%s:50020' % intf[0])
                self.params[mis] = val
                self.log.debug("%s not set. using  %s" % (mis, val))
            else:
                self.log.warn("could not set %s. no intf found for namenode")
        else:
            self.log.warn("Variable %s not found in service defaults" % mis) ## TODO is warn enough?
            return True ## not_mis_found

    def start_work_service_master(self):
        """Start service on master"""
        self.set_niceness(1, 2, 0, 'socket:0')
        if self.format_hdfs:
            self.log.info("Formatting HDFS")
            name_dir = self.params.get('dfs.name.dir', None)
            if name_dir:
                dest_dir = "%s.renamebeforeformat" % name_dir
                self.log.debug('Namedir %s found during format. Going to rename it to %s.' % (name_dir, dest_dir))
                os.rename("%s" % name_dir, dest_dir)

            formatcommand = FormatHdfs()
            formatcommand.run()
        else:
            self.log.debug("No HDFS format")

        self.log.info("Start namenode service on master.")
        command = NameNode(self.daemon_script, start=True)
        command.run()

    def start_work_service_slaves(self):
        """Run start_service on slaves"""
        self.set_niceness(5, 2, 3, 'socket:0')
        self.log.info("Start datanode service on slaves.")
        command = DataNode(self.daemon_script, start=True)
        command.run()

    def stop_work_service_master(self):
        """Stop service on master"""
        self.log.info("Stop namenode service on master.")
        command = NameNode(self.daemon_script, start=False)
        command.run()


    def stop_work_service_slaves(self):
        """Run start_service on slaves"""
        self.log.info("Stop datanode service on slaves.")
        command = DataNode(self.daemon_script, start=False)
        command.run()

