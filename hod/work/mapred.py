from hod.work.work import Work
from hod.work.hadoop import Hadoop
from hod.config.mapred import MapredOpts

from hod.config.customtypes import *

from vsc import fancylogger
fancylogger.setLogLevelDebug()

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
        elif mis in ('mapred.map.tasks',):
            mapfactor = len(self.thisnode.usablecores)
            tasks = int(len(self.allnodes) * mapfactor)
            self.log.debug("%s not set. using  %s" % (mis, tasks))
            self.params[mis] = tasks
        elif mis in ('mapred.reduce.tasks',):
            mapfactor = 2
            tasks = int(len(self.allnodes) * mapfactor)
            self.log.debug("%s not set. using  %s" % (mis, tasks))
            self.params[mis] = tasks
        else:
            self.log.warn("Variable %s not found in service_defaults" % mis) ## TODO is warn enough?
            return True ## not_mis_found
