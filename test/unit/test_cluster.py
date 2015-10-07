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

import os.path
import unittest
from mock import patch, Mock
from contextlib import contextmanager
from cStringIO import StringIO

import hod.cluster as hc
from hod.rmscheduler.rm_pbs import PbsJob

def _mock_open(**kwargs):
    """
    Hijack calls to `open` using filename=StringIO() arguments so we can
    verify the contents later.
    """
    @contextmanager
    def inner(x, *args):
        yield kwargs.get(os.path.basename(x), open(x, *args))
    return inner


class TestCluster(unittest.TestCase):
    """Tests for the hod.cluster module."""
    def test_is_valid_label(self):
        self.assertTrue(hc.is_valid_label('my-batch-job'))
        self.assertFalse(hc.is_valid_label('my/batch-job'))
        self.assertFalse(hc.is_valid_label('/mybatch-job'))
        self.assertFalse(hc.is_valid_label('mybatch-job/'))

    def test_validate_label(self):
        self.assertTrue(hc.validate_label('my-batch-job', ['your-batch-job']))
        self.assertFalse(hc.validate_label('my-batch-job', ['my-batch-job']))
        self.assertTrue(hc.validate_label('my-batch-job', []))
        self.assertFalse(hc.validate_label('my/batch-job', ['my-batch-job']))
        self.assertFalse(hc.validate_label('my/batch-job', ['your-batch-job', 'my-batch-job']))
        self.assertFalse(hc.validate_label('/mybatch-job', ['mybatch-job']))
        self.assertFalse(hc.validate_label('/mybatch-job', ['/mybatch-job']))

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

    def test_mk_cluster_info_dict(self):
        jobs = [PbsJob('123', 'R', 'host1'), PbsJob('abc', 'Q', '')]
        expected = [hc.ClusterInfo('banana', '123', jobs[0]), hc.ClusterInfo('apple', 'abc', jobs[1])]
        with patch('hod.cluster.cluster_jobid', side_effect=lambda lbl: dict(banana='123', apple='abc')[lbl]):
            self.assertEqual(expected, hc.mk_cluster_info_dict(['banana', 'apple'], jobs))

    def test_mk_cluster_info(self):
        jobs = [PbsJob('123', 'R', 'host1'), PbsJob('abc', 'Q', '')]
        jobid_file = StringIO()
        with patch('hod.cluster.cluster_jobid', side_effect=lambda lbl: dict(banana='123', apple='abc')[lbl]):
            with patch('os.makedirs'):
                with patch('__builtin__.open', side_effect=_mock_open(jobid=jobid_file)):
                    hc.mk_cluster_info('banana', jobs[0].jobid)
                    self.assertEqual(jobid_file.getvalue(), '123')

    def test_save_cluster_info(self):
        env_file = StringIO()
        with patch('hod.cluster.cluster_jobid', side_effect=lambda lbl: dict(banana='123', apple='abc')[lbl]):
            with patch('hod.cluster.cluster_info_exists', return_value=True):
                with patch('hod.cluster.generate_cluster_env_script', return_value='my script'):
                    with patch('__builtin__.open', side_effect=_mock_open(env=env_file)):
                        hc.save_cluster_info(dict(label='banana',
                            hadoop_conf_dir='hadoop', hod_localworkdir='localworkdir', modules=''))
                        self.assertTrue(env_file.getvalue(), 'my script')

    def test_save_cluster_info_mk_cluster_info(self):
        jobid_file = StringIO()
        env_file = StringIO()
        with patch('hod.cluster.cluster_jobid', side_effect=lambda lbl: dict(banana='123', apple='abc')[lbl]):
            with patch('hod.cluster.cluster_info_exists', return_value=False):
                with patch('hod.cluster.generate_cluster_env_script', return_value='my script'):
                    with patch('os.makedirs'):
                        with patch('__builtin__.open', side_effect=_mock_open(jobid=jobid_file, env=env_file)):
                            hc.save_cluster_info(dict(label='banana',
                                hadoop_conf_dir='hadoop', hod_localworkdir='localworkdir', modules=''))
                            self.assertTrue(env_file.getvalue(), 'my script')
