#!/usr/bin/env python

from hod.hodproc import Slave, HadoopMaster
from hod.mpiservice import MASTERRANK

if __name__ == '__main__':
    from mpi4py import MPI

    if MPI.COMM_WORLD.rank == MASTERRANK:
        serv = HadoopMaster()
    else:
        serv = Slave()

    try:
        serv.run_dist()

        serv.stop_service()
    except:
        serv.log.exception("Main HanythingOnDemand failed")


