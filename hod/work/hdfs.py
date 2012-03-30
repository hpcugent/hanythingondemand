from hod.work.work import Work
from hod.work.hadoop import Hadoop
from hod.config.hdfs import HdfsOpts

from hod.config.customtypes import *

from vsc import fancylogger
fancylogger.setLogLevelDebug()

import os

class Hdfs(HdfsOpts, Hadoop):
    """Base Hdfs work class"""
    def __init__(self, ranks, shared):
        Work.__init__(self, ranks) ## don't use Hadoop.__init__, better to redo Hadoop.__init__ with work + opts
        HdfsOpts.__init__(self, shared)

    def set_service_defaults(self, mis):
        """Set service specific default"""
        self.log.debug("Setting servicedefaults for %s" % mis)
        if mis in ('dfs.name.dir',):
            tmpdir = os.path.join(self.basedir, 'name')
            self.log.debug("%s not set. using  %s" % (mis, tmpdir))
            self.params[mis] = Directories(tmpdir)
        elif mis in ('dfs.data.dir',):
            tmpdir = os.path.join(self.basedir, 'data')
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

