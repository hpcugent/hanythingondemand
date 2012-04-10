from vsc import fancylogger
fancylogger.setLogLevelDebug()


from hod.work.work import Work
from hod.work.hadoop import Hadoop
from hod.config.client import ClientOpts


class Client(ClientOpts, Hadoop):
    """This class handles all client config and (if needed) extra services"""
    def __init__(self, ranks, shared):
        Work.__init__(self, ranks) ## don't use Hadoop.__init__, better to redo Hadoop.__init__ with work + opts
        ClientOpts.__init__(self, shared)

    def start_work_service_master(self):
        """Start the sshd server"""
        self.log.debug("Starting sshd server")
        self.sshdstart.run()


    def stop_work_service_master(self):
        """Stop the sshd server"""
        self.log.debug("Stopping sshd server")
        self.sshdstop.run()
