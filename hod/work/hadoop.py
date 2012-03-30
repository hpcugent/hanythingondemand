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

    def prepare_location(self):
        """prepare the location: make directories etc"""

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
        self.make_cfg()

    def start_service_master(self):
        """Start the Hadoop service"""

    def post_start_master(self):
        """Run after start_service_master"""

    def post_start_all(self):
        """Run after start_service"""

    def stop_service_master(self):
        """Stop the Hadoop service"""

    def post_stop_master(self):
        """Run after start_service_master"""

    def post_stop_all(self):
        """Run after start_service"""

    def wait(self):
        """What to do between start and stop (and how stop is triggered."""

    def do_work(self):
        """Look for required code and prepare all"""
        self.log.debug("Do work start")

        self.prepare_work_cfg()
        self.prepare_location()

        self.barrier("Going to run master only")
        if self.rank == self.masterrank:
            self.start_service_master()
            self.post_start_master()

        self.barrier("Going to run post_start all")
        self.post_start_all()

        self.barrier("Going to wait all")
        self.wait()

        self.barrier("Going to stop ")
        if self.rank == self.masterrank:
            self.stop_service_master()
            self.post_stop_master()

        self.barrier("Going to run post_stop all")
        self.post_stop_all()

        self.log.debug("Do work end")
