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
import os

from mock import patch
from vsc.utils.testing import EnhancedTestCase

import hod.subcommands.clone as hsc

def mock_exists(found):
    real_exists = os.path.exists
    def _exists(path):
        filename = os.path.basename(path)
        if filename in found:
            return found[filename]
        return real_exists(path)
    return _exists

class TestCloneSubCommand(EnhancedTestCase):
    def test_run_no_args(self):
        app = hsc.CloneSubCommand()
        self.assertErrorRegex(SystemExit, '1', app.run, ['clone'])

    def test_run_one_arg(self):
        app = hsc.CloneSubCommand()
        self.assertErrorRegex(SystemExit, '1', app.run, ['clone', 'some-dist'])

    def test_run_two_args_good(self):
        app = hsc.CloneSubCommand()
        found = {'some-output': False, 'some-dist': True}
        with patch('os.path.exists', side_effect=mock_exists(found)):
            with patch('shutil.copytree'):
                self.assertEqual(0, app.run(['clone', 'some-dist', 'some-output']))

    def test_run_two_args_output_exists_dist_does_not_exist(self):
        app = hsc.CloneSubCommand()
        found = {'some-output': True, 'some-dist': False}
        with patch('os.path.exists', side_effect=mock_exists(found)):
            with patch('shutil.copytree'):
                self.assertErrorRegex(SystemExit, '1', app.run, ['clone', 'some-dist', 'some-output'])

    def test_run_two_args_dist_not_found(self):
        app = hsc.CloneSubCommand()
        found = {'some-output': False, 'some-dist': False}
        with patch('os.path.exists', side_effect=mock_exists(found)):
            with patch('shutil.copytree'):
                self.assertErrorRegex(SystemExit, '1', app.run, ['clone', 'some-dist', 'some-output'])
