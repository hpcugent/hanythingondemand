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

import hod.applications.pbs as hap

from mock import patch

class TestCreatePbsApplication(unittest.TestCase):
    @pytest.mark.xfail(reason="Requires easybuild environment")
    def test_run_no_args(self):
        with patch('hod.applications.pbs.PbsHodJob'):
            app = hap.CreatePbsApplication()
            self.assertRaises(ValueError, app.run, [])

    @pytest.mark.xfail(reason="Requires easybuild environment")
    def test_run_with_args(self):
        with patch('hod.applications.pbs.PbsHodJob'):
            app = hap.CreatePbsApplication()
            app.run(['--config=hod.conf', '--workdir=workdir'])

    def test_run_with_dist_arg(self):
        with patch('hod.applications.pbs.PbsHodJob'):
            app = hap.CreatePbsApplication()
            app.run(['--dist=Hadoop-2.3.0', '--workdir=workdir'])

    def test_run_fails_with_config_and_dist_arg(self):
        with patch('hod.applications.pbs.PbsHodJob'):
            app = hap.CreatePbsApplication()
            self.assertRaises(ValueError, app.run, 
                    ['--config=hod.conf', '--dist=Hadoop-2.3.0', '--workdir=workdir'])

    def test_usage(self):
        app = hap.CreatePbsApplication()
        usage = app.usage()
        self.assertTrue(isinstance(usage, basestring))
