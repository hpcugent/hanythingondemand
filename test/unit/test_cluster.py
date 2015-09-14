# #
# Copyright 2009-2015 Ghent University
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
# #
"""
@author: Ewan Higgs (Universiteit Gent)
"""

import unittest
from mock import patch, Mock

import hod.cluster as hc
from hod.rmscheduler.rm_pbs import PbsJob

class TestCluster(unittest.TestCase):
    """Tests for the hod.cluster module."""
    def test_cluster_info_dir(self):
        with patch('os.getenv', lambda x, *args: dict(HOME='/home/myname', XDG_CONFIG_HOME='/home/myname/.config')[x]):
            self.assertEqual('/home/myname/.config/hod.d', hc.cluster_info_dir())

    def test_known_cluster_labels(self):
        with patch('hod.cluster.cluster_info_dir', return_value='/'):
            with patch('os.path.exists', return_value=True):
                with patch('os.listdir', return_value=['a']):
                    self.assertEqual(['a'], hc.known_cluster_labels())

    def test_known_cluster_labels_not_found(self):
        with patch('hod.cluster.cluster_info_dir', return_value='/'):
            with patch('os.path.exists', return_value=False):
                self.assertEqual([], hc.known_cluster_labels())
            

    def test_cluster_info(self):
        with patch('hod.cluster.cluster_info_dir', return_value='/'):
            with patch('hod.cluster.known_cluster_labels', return_value=['1234', 'banana']):
                with patch('os.path.exists', return_value=True):
                    self.assertEqual('/1234/jobid', hc._cluster_info('1234', 'jobid'))

    def test_cluster_info_no_label_found(self):
        with patch('hod.cluster.cluster_info_dir', return_value='/'):
            with patch('hod.cluster.known_cluster_labels', return_value=['banana']):
                with patch('os.path.exists', return_value=True):
                    self.assertRaises(ValueError, hc._cluster_info, '1234', 'jobid')

    def test_cluster_info_no_env_file(self):
        with patch('hod.cluster.cluster_info_dir', return_value='/'):
            with patch('hod.cluster.known_cluster_labels', return_value=['1234']):
                with patch('os.path.exists', return_value=False):
                    self.assertRaises(ValueError, hc._cluster_info, '1234', 'jobid')

    def test_find_pbsjob(self):
        expected = PbsJob('123', 'R', 'host')
        self.assertEqual(expected.jobid, hc._find_pbsjob('123', [PbsJob('123', 'R', 'host'), PbsJob('abc', 'Q', '')]).jobid)
        self.assertEqual(None, hc._find_pbsjob('xyz', [PbsJob('123', 'R', 'host'), PbsJob('abc', 'Q', '')]))

    def test_find_pbsjob_multiple(self):
        jobs = [PbsJob('123', 'R', 'host1'), PbsJob('abc', 'Q', '')]
        self.assertEqual(jobs[0], hc._find_pbsjob('123', jobs))
        self.assertEqual(jobs[1], hc._find_pbsjob('abc', jobs))

    def test_mk_cluster_info(self):
        jobs = [PbsJob('123', 'R', 'host1'), PbsJob('abc', 'Q', '')]
        expected = [hc.ClusterInfo('banana', '123', jobs[0]), hc.ClusterInfo('apple', 'abc', jobs[1])]
        with patch('hod.cluster.cluster_jobid', side_effect=lambda lbl: dict(banana='123', apple='abc')[lbl]):
            self.assertEqual(expected, hc.mk_cluster_info(['banana', 'apple'], jobs))
