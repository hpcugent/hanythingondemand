#!/usr/bin/env python
# ##
# Copyright 2009-2013 Ghent University
#
# This file is part of hanythingondemand
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/hanythingondemand
#
# hanythingondemand is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# hanythingondemand is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hanythingondemand. If not, see <http://www.gnu.org/licenses/>.
"""
Main hanythingondemand script, should be invoked in a job

@author: Stijn De Weirdt
"""
from hod.config.hodoption import HodOption
from hod.hodproc import Slave, HadoopMaster
from hod.mpiservice import MASTERRANK

from mpi4py import MPI

options = HodOptions()

if MPI.COMM_WORLD.rank == MASTERRANK:
    serv = HadoopMaster(options)
else:
    serv = Slave(options)

try:
    serv.run_dist()

    serv.stop_service()
except:
    serv.log.exception("Main HanythingOnDemand failed")
