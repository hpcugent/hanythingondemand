from hod.work.work import Work
from hod.config.hadoopcfg import HadoopCfg
from hod.config.hadoopopts import HadoopOpts

import os, pwd

from vsc import fancylogger
fancylogger.setLogLevelDebug()


class Hadoop(Work):
    """Base Hadoop work class"""
    def __init__(self, ranks, cfg=HadoopCfg, opts=HadoopOpts):
        Work.__init__(self, ranks)

        self.cfg = cfg()
        self.opts = opts()

    def prepare_location(self):
        """prepare the location: make directories etc"""

    def prepare_cfg(self):
        """prepare the config: collect the parameters and make the necessary xml cfg files"""
        self.cfg.run()
        ## set hadoophome in opts
        self.opts.hadoophome = self.cfg.hadoophome
        if self.opts.confdir is None:
            self.opts.confdir = os.path.join('/tmp', 'hod', pwd.getpwuid(os.getuid())[0])
        self.opts.make_cfg()

    def prepare_env(self):
        """prepare the environment: collect the parameters and make env vars"""

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

        self.prepare_cfg()
        self.prepare_env()
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

