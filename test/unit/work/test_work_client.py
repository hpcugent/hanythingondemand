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
import hod.work.client as hwc
import unittest

class HodWorkLocalClientTestCase(unittest.TestCase):
    '''Test LocalClient functions'''
    # TODO: Get these tests working

    def test_localclient_init(self):
        '''test LocalClient init function'''
        o = hwc.LocalClient([0], {})

    def test_localclient_start_work_service_master(self):
        '''test LocalClient start_work_service_master'''
        o = hwc.LocalClient([0], {})
        #o.start_work_service_master()

    def test_localclient_stop_work_service_master(self):
        '''test LocalClient stop_work_service_master'''
        o = hwc.LocalClient([0], {})
        #o.stop_work_service_master()

class HodWorkRemoteClientTestCase(unittest.TestCase):
    '''Test RemoteClient functions'''

    def test_remoteclient_init(self):
        '''test RemoveClient init function'''
        o = hwc.RemoteClient([0], {})

    def test_remoteclient_start_work_service_master(self):
        '''test RemoteClient start_work_service_master'''
        o = hwc.RemoteClient([0], {})
        #o.start_work_service_master()

    def test_remoteclient_stop_work_service_master(self):
        '''test RemoteClient stop_work_service_master'''
        o = hwc.RemoteClient([0], {})
        #o.start_work_service_master()
