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
import hod.work.mapred as hwm
from hod.mpiservice import MpiService
from hod.config.mapred import MapredOpts

class HodWorkMapredTestCase(unittest.TestCase):
    '''Test Mapred worker functions'''

    def test_work_mapred_init(self):
        '''test Hbase init function'''
        o = hwm.Mapred(MapredOpts({}))

    def test_work_mapred_set_service_defaults_localdir(self):
        '''test Hbase set_service_defaults function'''
        o = hwm.Mapred(MapredOpts({}, 'basedir'))
        o.allnodes = [0]
        o.set_service_defaults('mapred.local.dir')

    def test_work_mapred_set_service_defaults_jobtracker(self):
        '''test Hbase set_service_defaults function'''
        o = hwm.Mapred(MapredOpts({}, 'basedir'))
        o.svc = MpiService()
        o.set_service_defaults('mapred.job.tracker')

    def test_work_mapred_set_service_defaults_reduce_tasks(self):
        '''test Hbase set_service_defaults function'''
        o = hwm.Mapred(MapredOpts({}, 'basedir'))
        o.allnodes = [0]
        o.set_service_defaults('mapred.reduce.tasks')

    def test_work_mapred_set_service_defaults_reduce_tasks_maximum(self):
        '''test Hbase set_service_defaults function'''
        o = hwm.Mapred(MapredOpts({}, 'basedir'))
        o.allnodes = [0]
        o.set_service_defaults('mapred.tasktracker.reduce.tasks.maximum')

    def test_work_mapred_set_service_defaults_notfound(self):
        '''test Hbase set_service_defaults function'''
        opts = MapredOpts({}, 'basedir')
        opts.basic_cfg()
        o = hwm.Mapred(opts)
        o.allnodes = [0]
        o.set_service_defaults('mapred.notfound')

    def test_work_mapred_start_work_service_master(self):
        '''test Hbase start_work_service_master function'''
        opts = MapredOpts({}, 'basedir')
        opts.basic_cfg()
        o = hwm.Mapred(opts)
        with patch('hod.work.mapred.Jobtracker'):
            o.start_work_service_master()

    def test_work_mapred_start_work_service_slaves(self):
        '''test Hbase start_work_service_slaves function'''
        opts = MapredOpts({}, 'basedir')
        opts.basic_cfg()
        o = hwm.Mapred(opts)
        with patch('hod.work.mapred.Tasktracker'):
            o.start_work_service_slaves()

    def test_work_mapred_stop_work_service_master(self):
        '''test Hbase stop_work_service_master function'''
        opts = MapredOpts({}, 'basedir')
        opts.basic_cfg()
        o = hwm.Mapred(opts)
        with patch('hod.work.mapred.Jobtracker'):
            o.stop_work_service_master()

    def test_work_mapred_stop_work_service_slaves(self):
        '''test Hbase stop_work_service_slaves function'''
        opts = MapredOpts({}, 'basedir')
        opts.basic_cfg()
        o = hwm.Mapred(opts)
        with patch('hod.work.mapred.Tasktracker'):
            o.stop_work_service_slaves()
