
#
# Copyright 2012 Stijn De Weirdt
# 
# This file is part of HanythingOnDemand,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
from hod.work.work import Work
from hod.work.hadoop import Hadoop
from hod.config.mapred import MapredOpts

from hod.config.customtypes import *

from vsc import fancylogger


from hod.commands.hadoop import Jobtracker, Tasktracker

import os


class Mapred(MapredOpts, Hadoop):
    """Base Mapred work class"""
    def __init__(self, ranks, shared):
        Work.__init__(self, ranks)  ## don't use Hadoop.__init__, better to redo Hadoop.__init__ with work + opts
        MapredOpts.__init__(self, shared)


    def set_service_defaults(self, mis):
        """Set service specific default"""
        self.log.debug("Setting servicedefaults for %s" % mis)
        if mis in ('mapred.local.dir',):
            tmpdir = os.path.join(self.basedir, 'mapredlocal')
            self.log.debug("%s not set. using  %s" % (mis, tmpdir))
            self.params[mis] = Directories(tmpdir)
        elif mis in ('mapred.job.tracker',):
            intf = self.interface_to_nn()
            if intf:
                val = HostnamePort('%s:9000' % intf[0])
                self.params[mis] = val
                self.log.debug("%s not set. using  %s" % (mis, val))
            else:
                self.log.warn("could not set %s. no intf found for namenode")
        elif mis in ('mapred.map.tasks', 'mapred.tasktracker.map.tasks.maximum',):
            if mis.endswith('maximum'):
                tasks = int(len(self.thisnode.usablecores) / 2) ## avg 2 cores per task
            else:
                mapfactor = len(self.thisnode.usablecores) * 2 ##
                tasks = int(len(self.allnodes) * mapfactor)
            self.log.debug("%s not set. using  %s" % (mis, tasks))
            self.params[mis] = tasks
        elif mis in ('mapred.reduce.tasks', 'mapred.tasktracker.reduce.tasks.maximum',):
            mapfactor = 2
            if mis.endswith('maximum'):
                tasks = int(mapfactor * 1.75) ## total number of reduce tasks is maximum*number of nodes
            else:
                tasks = int(len(self.allnodes) * mapfactor)
            self.log.debug("%s not set. using  %s" % (mis, tasks))
            self.params[mis] = tasks
        else:
            self.log.warn("Variable %s not found in service_defaults" % mis) ## TODO is warn enough?
            return True ## not_mis_found

    def start_work_service_master(self):
        """Start service on master"""
        self.set_niceness(4, 2, 3, 'socket:0')
        self.log.info("Start jobtracker service on master.")
        command = Jobtracker(self.daemon_script, start=True)
        command.run()


    def start_work_service_slaves(self):
        """Run start_service on slaves"""
        self.set_niceness(15, 2, 7)
        self.log.info("Start tasktracker service on slaves.")
        command = Tasktracker(self.daemon_script, start=True)
        command.run()

    def stop_work_service_master(self):
        """Stop service on master"""
        self.log.info("Stop jobtracker service on master.")
        command = Jobtracker(self.daemon_script, start=False)
        command.run()


    def stop_work_service_slaves(self):
        """Run start_service on slaves"""
        self.log.info("Stop tasktracker service on slaves.")
        command = Tasktracker(self.daemon_script, start=False)
        command.run()

