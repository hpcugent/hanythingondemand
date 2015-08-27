###
# Copyright 2009-2014 Ghent University
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
'''
@author Ewan Higgs (Universiteit Gent)
'''

import unittest

from mock import patch, Mock

import hod.local as hl
import hod.mpiservice as hm

class TestHodLocal(unittest.TestCase):
    def test_local_no_args(self):
        # create_env_file is not implemented yet.
        self.assertRaises(NotImplementedError, hl.main, [])

    def test_master_rank(self):
        with patch('mpi4py.MPI.COMM_WORLD', Mock(rank=hm.MASTERRANK)):
            # create_env_file is not implemented yet.
            self.assertRaises(NotImplementedError, hl.main, [])

    def test_slave_rank(self):
        with patch('mpi4py.MPI.COMM_WORLD', Mock(rank=hm.MASTERRANK + 1)):
            self.assertRaisesRegexp(SystemExit, '1', hl.main, [])
