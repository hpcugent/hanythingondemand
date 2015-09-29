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

from hod.subcommands.create import CreateSubCommand

from mock import patch

class TestCreateSubCommand(unittest.TestCase):
    @pytest.mark.xfail(reason="Requires easybuild environment")
    def test_run_no_args(self):
        with patch('hod.subcommands.create.PbsHodJob'):
            app = CreateSubCommand()
            self.assertRaises(ValueError, app.run, [])

    @pytest.mark.xfail(reason="Requires easybuild environment")
    def test_run_with_args(self):
        with patch('hod.subcommands.create.PbsHodJob'):
            app = CreateSubCommand()
            app.run(['--hodconf=hod.conf', '--workdir=workdir', '--hod-module=hanythingondemand'])

    def test_run_with_dist_arg(self):
        with patch('hod.subcommands.create.PbsHodJob'):
            with patch('hod.cluster.mk_cluster_info'):
                app = CreateSubCommand()
                app.run(['--dist=Hadoop-2.3.0', '--workdir=workdir', '--hod-module=hanythingondemand'])

    def test_run_fails_with_config_and_dist_arg(self):
        with patch('hod.subcommands.create.PbsHodJob'):
            app = CreateSubCommand()
            self.assertEqual(app.run(['--hodconf=hod.conf', '--dist=Hadoop-2.3.0', '--workdir=workdir', '--hod-module=hanythingondemand']), 1)

    def test_usage(self):
        app = CreateSubCommand()
        usage = app.usage()
        self.assertTrue(isinstance(usage, basestring))
