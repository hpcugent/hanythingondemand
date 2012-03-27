#!/usr/bin/env python
from mpi4py import MPI
import time


from vsc import fancylogger
fancylogger.setLogLevelDebug()

class Slave:
    """The slave class. This is what is spawned"""
    def __init__(self):
        """Basic initialisation."""
        try:
            self.comm = MPI.Comm.Get_parent() ## the intercommunicator between master(s) and spawned slave(s)
            self.size = self.comm.Get_size()
            self.rank = self.comm.Get_rank()
        except:
            self.comm = None
            self.size = -1
            self.rank = -1

        self.log = fancylogger.getLogger("%s %s of %s" % (self.__class__.__name__, self.rank, self.size))

        self.log.debug("Init with Parent comm size %d rank %d communicator %s" % (self.size, self.rank, self.comm))

        try:
            self.intracomm = MPI.COMM_WORLD ## the intracommunicator between spawned slave(s)
            self.intrasize = self.intracomm.Get_size()
            self.intrarank = self.intracomm.Get_rank()
        except:
            self.intracomm = None
            self.intrasize = -1
            self.intrarank = -1

        self.log.debug("Init with Parent intracomm size %d intrarank %d intracommunicator %s" % (self.intrasize, self.intrarank, self.intracomm))


        ## place a barrier on the communicator for finalizing all processes
        self.stopwithbarrier = True ## this needs to match the value for the spawning master
        self.stopwithintrabarrier = True

        self.workinitbarrier = True

        if not (self.stopwithbarrier or self.stopwithintrabarrier or self.workinitbarrier):
            # at least one barrier must be in place (i think)
            self.log.error("At least one barrier should be in place")

        self.work = None
        self.dowork = self.nowork


    def workinit(self):
        """Determine howmuch work there is to do."""
        work = None
        self.comm.bcast(work, root=0)
        self.log.debug("Received work %s" % work)
        self.work = work

        if self.workinitbarrier:
            self.log.debug("Waiting for barrier workinit")
            self.comm.barrier()
        else:
            self.log.debug("No workinit barrier")

        self.log.debug("Completed workinit")

    def stop(self):
        """Stop this slave"""
        self.log.debug("Stop communicator %s stopwithbarrier %s intracommunicator %s stopwithintrabarrier %s" % (self.comm, self.stopwithbarrier, self.intracomm, self.stopwithintrabarrier))
        #self.comm.Disconnect()
        if self.stopwithintrabarrier:
            self.intracomm.barrier()
        if self.stopwithbarrier:
            self.comm.barrier()

        del self.intracomm
        del self.comm

    def go(self):
        """This is called in main slave body"""

        self.log.debug("Begin go")

        try:
            self.workinit()

            self.dowork()
        except:
            self.log.exception("go failed to run.")

        self.stop()

        self.log.debug("End go")


    def nowork(self):
        """Do nothing"""
        self.log.debug("Doing no work")

    def setcommandwork(self):
        self.log.debug("Set commandwork")
        self.dowork = self.commandwork
        if not type(self.work) in (list, tuple,):
            self.work = [] ## default value is empty list

    def commandwork(self):
        """Process all work as commands"""
        for work in self.work:
            self.log.debug("Processing work %s" % (work))

            if not work.has_key('command'):
                self.log.error("No command for %s" % work)

            cmdrank = work.get('rank', [-2])
            self.log.debug("work cmdrank %s" % cmdrank)
            if -2 in cmdrank or self.intrarank in cmdrank:
                self.executecommand(work)
            else:
                self.log.debug("Not my rank %s in work %s" % (self.intrarank, work))
                work['ec'] = 0 # ok

        self.log.debug("Resulting work %s" % self.work)

    def executecommand(self, commanddict):
        """Command dict is a dictionary with at least one command=CommandClass pair"""
        if not commanddict.has_key('command'):
            self.log.error("No command for %s" % commanddict)

        res = 0


        commanddict['ec'] = res
        self.log.debug("Executed command %s with ec %s" % (commanddict, res))
        if not res == 0:
            self.log.error("Command failed with exitcode %s : %s" % (res, commanddict))


class TestSlave(Slave):
    """Slave class that matches the TestPythonSlave spawn class. It is the simplest implementation of a Command based execution process"""
    def __init__(self):
        Slave.__init__(self)
        self.setcommandwork()

        ## for testing

if __name__ == '__main__':
    s = TestSlave()
    s.go()
