###
# Copyright 2009-2014 Ghent University
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
'''
@author Ewan Higgs (Universiteit Gent)
'''

import unittest
from mock import MagicMock

import hod.options as ho

class TestOption(unittest.TestCase):
    def test_validate_pbs_option(self):
        options = MagicMock(workdir='/', dist='Hadoop', hod_module='hod', hodconf=None)
        self.assertTrue(ho.validate_pbs_option(options))

    def test_validate_genconfig_option_fails_with_config_and_dist(self):
        options = MagicMock(workdir='/', dist='Hadoop', hod_module='hod', hodconf='hod.conf')
        self.assertFalse(ho.validate_pbs_option(options))

    def test_validate_genconfig_option_fails_missing_dist_or_config(self):
        options = MagicMock(workdir='/', hod_module='')
        self.assertFalse(ho.validate_pbs_option(options))

    def test_validate_genconfig_option_fails_missing_workdir(self):
        options = MagicMock(dist='Hadoop', hod_module='hod')
        self.assertFalse(ho.validate_pbs_option(options))

    def test_validate_genconfig_option_fails_missing_hod_module(self):
        options = MagicMock(workdir='/', dist='Hadoop')
        self.assertFalse(ho.validate_pbs_option(options))

    def test_validate_genconfig_option(self):
        options = MagicMock(workdir='/', dist='Hadoop', hod_module='hod', hodconf=None)
        self.assertTrue(ho.validate_genconfig_option(options))

    def test_validate_fails_missing_dist_or_config(self):
        options = MagicMock(workdir='/')
        self.assertFalse(ho.validate_genconfig_option(options))
