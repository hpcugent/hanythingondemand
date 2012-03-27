#!/usr/bin/env python

from mpiservice import MpiService, MASTERRANK

from work import TestWorkA, TestWorkB

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


if __name__ == '__main__':
    from mpi4py import MPI

    if MPI.COMM_WORLD.rank == MASTERRANK:
        serv = Master()
    else:
        serv = Slave()

    try:
        import time

        time.sleep(1)

        serv.run_dist()

        serv.stop()
    except:
        serv.log.exception("Main failed")


