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
import os
import shutil
import pytest
import tempfile
import unittest

from hod.subcommands.batch import BatchSubCommand

from mock import patch

class TestBatchSubCommand(unittest.TestCase):
    @pytest.mark.xfail(reason="Requires easybuild environment")
    def test_run_no_args(self):
        with patch('hod.subcommands.batch.PbsHodJob'):
            app = BatchSubCommand()
            self.assertRaises(ValueError, app.run, [])

    @pytest.mark.xfail(reason="Requires easybuild environment")
    def test_run_with_hodconf_and_no_script(self):
        with patch('hod.subcommands.batch.PbsHodJob'):
            app = BatchSubCommand()
            self.assertEqual(1, app.run(['--hodconf=hod.conf', '--workdir=workdir', '--hod-module=hanythingondemand']))

    def test_run_fails_with_dist_and_no_script(self):
        with patch('hod.subcommands.batch.PbsHodJob'):
            app = BatchSubCommand()
            self.assertEqual(1, app.run(['--dist=Hadoop-2.3.0', '--workdir=workdir', '--hod-module=hanythingondemand']))

    def test_run_with_hodconf(self):
        with patch('hod.subcommands.batch.PbsHodJob'):
            with patch('hod.cluster.mk_cluster_info'):
                with patch('hod.cluster.validate_hodconf_or_dist', return_value=True):
                    app = BatchSubCommand()
                    # script *must* exist (hod batch will stat it, chmod if needed)
                    tmpdir = tempfile.mkdtemp()
                    script = os.path.join(tmpdir, 'some-script.sh')
                    with open(script, 'w') as f:
                        f.write('echo hello')
                    cwd = os.getcwd()
                    os.chdir(tmpdir)
                    self.assertEqual(0, app.run(['--dist=Hadoop-2.3.0', '--workdir=workdir',
                                                 '--hod-module=hanythingondemand', '--script=some-script.sh']))
                    shutil.rmtree(tmpdir)
                    os.chdir(cwd)

    def test_run_with_dist(self):
        with patch('hod.subcommands.batch.PbsHodJob'):
            with patch('hod.cluster.mk_cluster_info'):
                with patch('hod.cluster.validate_hodconf_or_dist', return_value=True):
                    app = BatchSubCommand()
                    # script *must* exist (hod batch will stat it, chmod if needed)
                    tmpdir = tempfile.mkdtemp()
                    script = os.path.join(tmpdir, 'some-script.sh')
                    with open(script, 'w') as f:
                        f.write('echo hello')
                    cwd = os.getcwd()
                    os.chdir(tmpdir)
                    self.assertEqual(0, app.run(['--dist=Hadoop-2.3.0', '--workdir=workdir',
                                                 '--hod-module=hanythingondemand', '--script=some-script.sh']))
                    shutil.rmtree(tmpdir)
                    os.chdir(cwd)

    def test_run_fails_with_config_and_dist_arg(self):
        with patch('hod.subcommands.batch.PbsHodJob'):
            with patch('hod.cluster.validate_hodconf_or_dist', return_value=True):
                app = BatchSubCommand()
                self.assertEqual(1, app.run(['--hodconf=hod.conf', '--dist=Hadoop-2.3.0',
                                             '--hod-module=hanythingondemand', '--workdir=workdir']))

    def test_usage(self):
        app = BatchSubCommand()
        usage = app.usage()
        self.assertTrue(isinstance(usage, basestring))
