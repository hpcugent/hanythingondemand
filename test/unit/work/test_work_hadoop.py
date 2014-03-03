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
import hod.work.hadoop as hwh

class HodWorkHadopoTestCase(unittest.TestCase):
    def test_work_hadoop_init(self):
        o = hwh.Hadoop([0], {})

    def test_work_hadoop_interface_to_nn(self):
        o = hwh.Hadoop([0], {})
        o.interface_to_nn()

    def test_work_hadoop_prepare_extra_work_cfg(self):
        o = hwh.Hadoop([0], {})
        o.prepare_extra_work_cfg() # TODO: Remove

    def test_work_hadoop_prepare_work_cfg(self):
        o = hwh.Hadoop([0], {})
        o.prepare_work_cfg()

    @unittest.expectedFailure
    def test_work_hadoop_use_sdp(self):
        o = hwh.Hadoop([0], {})
        o.use_sdp()

    @unittest.expectedFailure
    def test_work_hadoop_use_sdp_java(self):
        o = hwh.Hadoop([0], {})
        o.use_sdp_java()

    @unittest.expectedFailure
    def test_work_hadoop_use_sdp_libsdp(self):
        o = hwh.Hadoop([0], {})
        o.use_sdp_libsdp('intf')
