#!/usr/bin/env python

from mpi4py import MPI
import sys

from vsc import fancylogger
fancylogger.setLogLevelDebug()

class master:
    """The master class. This class will start the slaves and handout work."""
    def __init__(self):
        """Basic initialisation"""
        self.log = fancylogger.getLogger(self.__class__.__name__)

        try:
            self.comm = MPI.COMM_WORLD
            self.size = self.comm.Get_size()
            self.rank = self.comm.Get_rank()
        except:
            self.comm = None
            self.size = -1
            self.rank = -1

        self.log.debug("Init with COMM_WORLD size %d rank %d communicator %s" % (self.size, self.rank,self.comm))
        self.stopwithbarrier = True

    def stop_script(self):
        """Stop this master"""
        self.log.debug("Stop communicator %s stopwithbarrier %s"%(self.comm,self.stopwithbarrier))
        #self.comm.Disconnect()
        if self.stopwithbarrier:
            self.comm.barrier()
        del self.comm

class Spawn:
    """The Spawn class will spawn the slaves"""
    def __init__(self, exe, args):
        """Initialisation arguments determine executable to run and arguments of said executable"""
        self.log = fancylogger.getLogger(self.__class__.__name__)

        self.exe = exe
        self.args = args

        self.maxprocs = 2

        self.commself = None
        self.selfsize = None
        self.selfrank = None

        self.commclone = None
        self.clonesize = None
        self.clonerank = None

        self.comm = None
        self.size = None
        self.rank = None

        self.group = None
        self.groupsize = None
        self.grouprank = None

        self.stopwithbarrier = True
        self.workinitbarrier = True


        self.work = None
        self.dowork = None ## no work to be done is default 

    def runspawn(self, maxprocs=None):
        """Spawn the slaves"""

        if maxprocs is not None:
            self.maxprocs = maxprocs

        self.log.debug("runspawn going to start comm with exe %s args %s maxprocs %d" % (self.exe, self.args, self.maxprocs))
        
        self.commself = MPI.COMM_SELF
        self.selfsize = self.commself.Get_size()
        self.selfrank = self.commself.Get_rank()
        self.log.debug("runspawn with comm selfsize %d selfrank %s selfcommunicator %s" % (self.selfsize,self.selfrank,self.commself))

        self.commclone = self.commself.Clone()
        self.clonesize = self.commclone.Get_size()
        self.clonerank = self.commclone.Get_rank()
        self.log.debug("runspawn with comm clonesize %d clonerank %s clonecommunicator %s" % (self.clonesize,self.clonerank,self.commclone))
        

        self.comm = self.commclone.Spawn(self.exe,args=self.args,maxprocs=self.maxprocs) # this defines the intercommunicator
        self.size = self.comm.Get_remote_size()
        self.rank = self.comm.Get_rank()

        self.log.debug("runspawn with comm size %d rank %s communicator %s" % (self.size,self.rank,self.comm))

        self.group = self.comm.Get_remote_group()
        self.groupsize = self.group.Get_size()
        self.grouprank = self.group.Get_rank()
        
        self.log.debug("runspawn with group size %d group rank %s group %s" % (self.groupsize,self.grouprank,self.group))



    def go(self, whatwork=None):
        """Spawn the slaves and distribute the work"""
        if whatwork is not None:
            self.dowork = whatwork

        self.log.debug("Begin go")

        try:
            self.runspawn()

            self.doworkinit() ## always do init!

            if self.dowork is not None:
                self.dowork()

        except:
            self.log.exception("go failed to run.")

        self.stop_script()
        self.log.debug("End go")


    def doworkinit(self):
        """Communicate work details: type and amount"""

        root=MPI.ROOT
        self.log.debug("Send workinit root %s work %s" % (root,self.work))
        self.comm.bcast(self.work, root=root)

        if self.workinitbarrier:
            self.log.debug("Waiting for barrier workinit")
            self.comm.barrier()
        else:
            self.log.debug("No workinit barrier")
            
        self.log.debug("Completed workinit")


    def simplework(self):
        """Simple list of work to process"""
        for w in self.work:
            res = None
            self.log.debug("Send work %s" % w)
            self.comm.bcast(w, root=MPI.ROOT)
            self.comm.gather(res, root=MPI.ROOT)
            self.log.debug("Get result %s" % res)

    def stop_script(self):
        """Stop this spawn"""
        self.log.debug("Stop communicator %s stopwithbarrier %s"%(self.comm,self.stopwithbarrier))
        #self.comm.Disconnect()
        if self.stopwithbarrier:
            self.comm.barrier()
        del self.comm

class SpawnPython(Spawn):
    """Spawn python slaves. Exe is the current python executable path; args are the scripts to run"""
    def __init__(self, args):
        """Pass current python as exe"""
        Spawn.__init__(self, exe=sys.executable, args=args)

class TestPythonSlave(SpawnPython):
    """Simple test class"""
    def __init__(self):
        SpawnPython.__init__(self,args=['s.py'])
        self.work=[{'command':'test1'},
                   {'nocommand':'shouldfail'}, ## this command should fail due to missing command key
                   {'command':'rank1','rank':1} ## only on rank 1
                   ]

if __name__ == '__main__':
    m = master()

    s = TestPythonSlave()
    s.go()
    ## this is blocking
    #s2 = SpawnPython(args=['s.py','test'])
    #s2.go()

    m.log.info("all went well")
    m.stop_script()
