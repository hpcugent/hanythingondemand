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

from mock import patch, MagicMock

from vsc.utils.testing import EnhancedTestCase

from ..util import capture
import hod.subcommands.relabel as hsr

class TestRelabelSubCommand(EnhancedTestCase):
    def test_run_no_args(self):
        app = hsr.RelabelSubCommand()
        self.assertErrorRegex(SystemExit, '1', app.run, [])

    def test_run_success(self):
        with patch('hod.cluster.known_cluster_labels', return_value=['abc']):
            with patch('hod.cluster.cluster_info_dir', return_value='/path'):
                with patch('shutil.move', MagicMock()) as move_fn:
                    app = hsr.RelabelSubCommand()
                    app.run(['relabel', 'abc', 'xyz'])
                    move_fn.assert_called_with('/path/abc', '/path/xyz')

    def test_run_oserror(self):
        with patch('hod.cluster.known_cluster_labels', return_value=['abc']):
            with patch('hod.cluster.cluster_info_dir', return_value='/path'):
                with patch('shutil.move', side_effect=OSError('bad')):
                    app = hsr.RelabelSubCommand()
                    self.assertErrorRegex(SystemExit, '1', app.run, ['relabel', 'abc', 'xyz'])

    def test_run_ioerror(self):
        with patch('hod.cluster.known_cluster_labels', return_value=['abc']):
            with patch('hod.cluster.cluster_info_dir', return_value='/path'):
                with patch('shutil.move', side_effect=IOError('bad')):
                    app = hsr.RelabelSubCommand()
                    self.assertErrorRegex(SystemExit, '1', app.run, ['relabel', 'abc', 'xyz'])

    def test_usage(self):
        app = hsr.RelabelSubCommand()
        usage = app.usage()
        self.assertTrue(isinstance(usage, basestring))
