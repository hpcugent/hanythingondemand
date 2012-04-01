from hod.work.work import Work
from hod.config.hadoopopts import HadoopOpts

import os, pwd

from vsc import fancylogger
fancylogger.setLogLevelDebug()


class Hadoop(Work, HadoopOpts):
    """Base Hadoop work class"""
    def __init__(self, ranks, shared):
        Work.__init__(self, ranks)
        HadoopOpts.__init__(self, shared)

    def interface_to_nn(self):
        """What interface can reach the namenode"""
        nn = self.params.get('fs.default.name', self.default_fsdefault)
        if None in nn:
            self.log.error("No namenode set")
            return None

        intf = self.thisnode.ip_interface_to(nn.hostname)
        if intf:
            self.log.debug("namenode can be reached by intf %s" % intf)
            return intf
        else:
            self.log.error("namenode %s cannot be reached by any of the local interfaces %s" % (nn, self.thisnode.network))

    def prepare_extra_work_cfg(self):
        """Add some custom parameters"""

    def prepare_work_cfg(self):
        """prepare the config: collect the parameters and make the necessary xml cfg files"""
        self.basic_cfg()
        if self.basedir is None:
            self.basedir = os.path.join('/tmp', 'hod', pwd.getpwuid(os.getuid())[0], self.name)

        self.prepare_extra_work_cfg()

        if None in self.default_fsdefault:
            self.log.error("Primary nameserver still not set.")

        ## make the cfg
        self.make_opts_env_cfg()


