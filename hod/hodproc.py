#!/usr/bin/env python

from hod.mpiservice import MpiService, MASTERRANK

from hod.work.work import TestWorkA, TestWorkB
from hod.work.mapred import Mapred
from hod.work.hdfs import Hdfs

from vsc import fancylogger
fancylogger.setLogLevelDebug()


class Master(MpiService):
    """Basic Master"""

    def distribution(self):
        """Master makes the distribution"""
        ## example part one on half one, part 2 on second half
        self.dists = []

        allranks = range(self.size)
        self.dists.append([TestWorkA, allranks[:self.size / 2]])
        self.dists.append([TestWorkB, allranks[self.size / 2:]])

class Slave(MpiService):
    """Basic Slave"""

class HadoopMaster(MpiService):
    """Basic Master"""

    def distribution(self):
        """Master makes the distribution"""
        ## example part one on half one, part 2 on second half (make sure one is always started)
        self.dists = []

        allranks = range(self.size)
        lim = self.size / 2
        self.dists.append([Hdfs, allranks[:max(lim, 1)]]) ## for lim == 0, make sure Hdfs is started
        self.dists.append([Mapred, allranks[lim:]])



if __name__ == '__main__':
    from mpi4py import MPI

    if MPI.COMM_WORLD.rank == MASTERRANK:
        serv = HadoopMaster()
    else:
        serv = Slave()

    try:
        import time

        time.sleep(1)

        serv.run_dist()

        serv.stop_service()
    except:
        serv.log.exception("Main failed")


