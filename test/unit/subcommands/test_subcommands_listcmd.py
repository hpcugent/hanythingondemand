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
from mock import patch, Mock
from ..util import capture
from hod.subcommands.listcmd import ListSubCommand

class TestListSubCommand(unittest.TestCase):
    def test_run(self):
        app = ListSubCommand()
        app.run([])

    def test_run_good(self):
        import hod.rmscheduler.rm_pbs as rm_pbs
        job = rm_pbs.PbsJob('good-jobid', 'good-jid', 'good-jstate', 'good-host', 'good-state')
        with patch('hod.rmscheduler.rm_pbs.Pbs', return_value=Mock(state=lambda: [job])):
            app = ListSubCommand()
            with capture(app.run, []) as (out, err):
                self.assertEqual(out, 'Found 1 job Id good-jobid State good-state Node good-host\n')

    def test_usage(self):
        app = ListSubCommand()
        usage = app.usage()
        self.assertTrue(isinstance(usage, basestring))

