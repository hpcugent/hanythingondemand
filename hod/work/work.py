from vsc import fancylogger
fancylogger.setLogLevelDebug()

from hod.mpiservice import MpiService

class Work(MpiService):
    """Basic work class"""
    def __init__(self, ranks, shared=None):
        self.log = fancylogger.getLogger(self.__class__.__name__)
        MpiService.__init__(self, initcomm=False, log=self.log)

        self.shared = shared ## shared is something that can be shared between work (eg common information)

        self.allranks = ranks

        self.commands = {} ## dict with command : list of ranks

    def run(self, comm):
        """Setup MPI comm and do_work"""
        self.init_comm(comm, startwithbarrier=True)

        self.log.debug("run do_work")
        self.do_work()

        self.stop_service()

    def do_work(self):
        """Actually do something. To be implemented by derivative classes"""
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
