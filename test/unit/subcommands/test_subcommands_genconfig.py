#!/usr/bin/env python
# #
# Copyright 2009-2016 Ghent University
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
from mock import patch, Mock, MagicMock

from hod.subcommands.genconfig import GenConfigSubCommand

class TestGenconfigSubCommand(unittest.TestCase):
    def test_run(self):
        app = GenConfigSubCommand()
        mpi = Mock(COMM_WORLD=0, Get_size=lambda:1)
        mock_cfg = Mock(modules=lambda:[], master_env=[], hodconfdir='',
                service_files=[])
        with patch('mpi4py.MPI', mpi):
            with patch('hod.hodproc._setup_config_paths'):
                with patch('hod.hodproc.resolve_config_paths', return_value='/'):
                    with patch('hod.hodproc.load_hod_config', return_value=mock_cfg):
                        with patch('hod.hodproc._setup_template_resolver', return_value=Mock()):
                            app.run(['--workdir=/no-path', '--hod-module=foo', '--dist=Some-Dist-1.2.3'])

    def test_run_no_hod_module(self):
        app = GenConfigSubCommand()
        mpi = Mock(COMM_WORLD=0, Get_size=lambda:1)
        mock_cfg = Mock(modules=lambda:[], master_env=[], hodconfdir='',
                service_files=[])
        with patch('mpi4py.MPI', mpi):
            with patch('hod.hodproc._setup_config_paths'):
                with patch('hod.hodproc.resolve_config_paths', return_value='/'):
                    with patch('hod.hodproc.load_hod_config', return_value=mock_cfg):
                        with patch('hod.hodproc._setup_template_resolver', return_value=Mock()):
                            app.run(['--workdir=/no-path', '--dist=Some-Dist-1.2.3'])

    def test_usage(self):
        app = GenConfigSubCommand()
        usage = app.usage()
        self.assertTrue(isinstance(usage, basestring))
