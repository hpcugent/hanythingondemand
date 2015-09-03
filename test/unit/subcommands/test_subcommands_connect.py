#!/usr/bin/env python
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
import pytest

import hod.rmscheduler.rm_pbs as rm_pbs
import hod.subcommands.connect as hsc

from ..util import capture, MockPbs

from mock import patch


def mock_getenv(var, dflt=None):
    if var == 'HOME':
        return '/home/user'
    elif var == 'XDG_CONFIG_HOME':
        return '/home/user/.config'
    else:
        return None

CLUSTERS = ['1234', 'old-finished-job']

def mock_listdir(path):
    return CLUSTERS

class TestCreateSubCommand(unittest.TestCase):
    @pytest.mark.xfail(reason="Requires easybuild environment")
    def test_run_no_args(self):
        app = hsc.ConnectSubCommand()
        self.assertRaisesRegexp(SystemExit, '1', app.run, [])

    def test_run_with_bad_jobid_arg(self):
        with patch('hod.rmscheduler.rm_pbs.Pbs', MockPbs):
            with patch('os.getenv', mock_getenv):
                with patch('os.listdir', mock_listdir):
                    app = hsc.ConnectSubCommand()
                    self.assertRaisesRegexp(SystemExit, '1', app.run, ['connect', 'not-a-job-id'])

    def test_run_with_queued_jobid_arg(self):
        with patch('hod.rmscheduler.rm_pbs.Pbs', MockPbs):
            with patch('os.getenv', mock_getenv):
                with patch('os.listdir', mock_listdir):
                    app = hsc.ConnectSubCommand()
                    self.assertRaisesRegexp(SystemExit, '1', app.run, ['connect', 'q123'])

    def test_run_with_held_jobid_arg(self):
        with patch('hod.rmscheduler.rm_pbs.Pbs', MockPbs):
            with patch('os.getenv', mock_getenv):
                with patch('os.listdir', mock_listdir):
                    app = hsc.ConnectSubCommand()
                    self.assertRaisesRegexp(SystemExit, '1', app.run, ['connect', 'h123'])


    @pytest.mark.xfail
    def test_run_with_good_jobid_arg(self):
        with patch('hod.rmscheduler.rm_pbs.Pbs', MockPbs):
            with patch('hod.subcommands.connect.os.execvp'):
                with patch('os.getenv', mock_getenv):
                    with patch('os.listdir', mock_listdir):
                        with patch('os.path.exists', return_value=True):
                            app = hsc.ConnectSubCommand()
                            self.assertEqual(app.run(['connect', '1234']), 0)

    @pytest.mark.xfail
    def test_run_with_check_msgs(self):
        with patch('hod.rmscheduler.rm_pbs.Pbs', MockPbs):
            with patch('hod.subcommands.connect.os.execvp'):
                with patch('os.getenv', mock_getenv):
                    with patch('sys.exit'):
                        with patch('hod.local.known_cluster_labels', return_value=CLUSTERS):
                            with patch('os.path.exists', return_value=True):
                                app = hsc.ConnectSubCommand()
                                with capture(app.run, ['connect']) as (out, err):
                                    self.assertEqual(out, '')
                                    self.assertEqual(err, 'No jobid provided.\n')
                                with capture(app.run, ['connect', 'not-a-job-id']) as (out, err):
                                    self.assertEqual(out, '')
                                    self.assertEqual(err, "Unknown cluster label 'not-a-job-id': ['1234', 'old-finished-job']\n")
                                with capture(app.run, ['connect', 'old-finished-job']) as (out, err):
                                    self.assertEqual(out, '')
                                    self.assertEqual(err, 'Job old-finished-job not found by pbs.\n')
                                with capture(app.run, ['connect', '1234']) as (out, err):
                                    self.assertEqual(out, '')
                                    self.assertEqual(err, '')
