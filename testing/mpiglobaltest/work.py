
#
# Copyright 2012 Stijn De Weirdt
# 
# This file is part of HanythingOnDemand,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
from vsc import fancylogger
fancylogger.setLogLevelDebug()

from mpiservice import MpiService

class Work(MpiService):
    def __init__(self, ranks):
        self.log = fancylogger.getLogger(self.__class__.__name__)
        MpiService.__init__(self, initcomm=False, log=self.log)

        self.allranks = ranks

        self.commands = {} ## dict with command : list of ranks

    def run(self, comm):
        self.init_comm(comm, startwithbarrier=True)

        self.log.debug("run do_work")
        self.do_work()

        self.stop_script()

    def do_work(self):
        """Reimplement"""
        self.log.error("No Work implemented.")

class SleepWork(Work):
    def do_work(self):
        """Just sleep"""
        sleeptime = 3
        self.log.debug("do_work: sleep %d" % sleeptime)

        import time
        time.sleep(sleeptime)

        self.log.debug("do_work: end sleep %d" % sleeptime)

class TestWorkA(SleepWork):
    """TestWorkA for testing"""

class TestWorkB(SleepWork):
    """TestWorkB for testing"""
