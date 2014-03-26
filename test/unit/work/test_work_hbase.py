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
import hod.work.hbase as hwh
from hod.config.hbase import HbaseOpts

class HodWorkHbaseTestCase(unittest.TestCase):
    '''Test Hbase worker functions'''

    def test_work_hbase_init(self):
        '''test Hbase init function'''
        o = hwh.Hbase(HbaseOpts({}))

    def test_work_hbase_set_service_defaults(self):
        '''test Hbase set_service_defaults'''
        o = hwh.Hbase(HbaseOpts({}))
        o.set_service_defaults('mis') # TODO: what is 'mis'? A string, but what?

    def test_work_hbase_start_work_service_master(self):
        '''test Hbase start_work_service_master'''
        o = hwh.Hbase(HbaseOpts({}))
        #o.start_work_service_master()

    def test_work_hbase_start_work_service_slaves(self):
        '''test Hbase start_work_service_slaves'''
        o = hwh.Hbase(HbaseOpts({}))
        #o.start_work_service_slaves()

    @unittest.expectedFailure
    def test_work_hbase_stop_work_service_master(self):
        '''test Hbase stop_work_service_master'''
        o = hwh.Hbase(HbaseOpts({}))
        o.stop_work_service_master()

    @unittest.expectedFailure
    def test_work_hbase_stop_work_service_slaves(self):
        '''test Hbase stop_work_service_slaves'''
        o = hwh.Hbase(HbaseOpts({}))
        o.stop_work_service_slaves()
