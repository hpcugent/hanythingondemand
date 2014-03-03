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
import unittest
import hod.work.hdfs as hwh

class HodWorkHDFSTestCase(unittest.TestCase):
    def test_work_hdfs_init(self):
        o = hwh.Hdfs([0], {})

    def test_work_hdfs_set_service_defaults(self):
        o = hwh.Hdfs([0], {})
        o.set_service_defaults('mis') # TODO: what is 'mis'? A string, but what?

    def test_work_hdfs_start_work_service_master(self):
        o = hwh.Hdfs([0], {})
        #o.locate_start_stop_daemon()
        #o.start_work_service_master()

    def test_work_hdfs_start_work_service_slaves(self):
        o = hwh.Hdfs([0], {})
        #o.locate_start_stop_daemon()
        #o.start_work_service_slaves()

    def test_work_hdfs_stop_work_service_master(self):
        o = hwh.Hdfs([0], {})
        #o.locate_start_stop_daemon()
        #o.stop_work_service_master()

    def test_work_hdfse_stop_work_service_slaves(self):
        o = hwh.Hdfs([0], {})
        #o.locate_start_stop_daemon()
        #o.stop_work_service_slaves()
