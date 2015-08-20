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

import hod.main as hm
import hod.subcommands.dists

class TestHodMain(unittest.TestCase):
    def test_main_no_args(self):
        self.assertRaises(SystemExit, hm.main, [])

    def test_main_bad_cmd(self):
        self.assertRaises(SystemExit, hm.main, ['hod', 'banana'])

    def test_main_good_cmd(self):
        hm.main(['hod', 'dists'])

    def test_main_help(self):
        self.assertRaises(SystemExit, hm.main, ['hod', '--help'])

    def test_usage(self):
        self.assertTrue(isinstance(hm.usage(), basestring))

    def test_init_bad_subcmd(self):
        cmd, opts = hm.init_subcmd(['hod', 'apricot'])
        self.assertEqual(cmd, None)
        self.assertEqual(opts, ['hod', 'apricot'])

    def test_init_bad_subcmd_option(self):
        cmd, opts = hm.init_subcmd(['hod', '--help'])
        self.assertEqual(cmd, None)
        self.assertEqual(opts, ['hod', '--help'])

    def test_init_good_subcmd(self):
        cmd, opts = hm.init_subcmd(['hod', 'dists'])
        self.assertTrue(isinstance(cmd, hod.subcommands.dists.DistsSubCommand))
        self.assertEqual(opts, None)

    def test_init_good_subcmd_options(self):
        cmd, opts = hm.init_subcmd(['hod', 'dists', '--someoptions'])
        self.assertTrue(isinstance(cmd, hod.subcommands.dists.DistsSubCommand))
        self.assertEqual(opts, None)
