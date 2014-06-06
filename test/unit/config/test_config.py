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
from mock import patch
import hod.config.config as hcc
from cStringIO import StringIO

class HodConfigConfig(unittest.TestCase):
    '''Test Config functions'''

    def test_resolve_templates(self):
        self.assertEqual(hcc._resolve_templates(dict(a=1)), dict(a=1))
        self.assertEqual(hcc._resolve_templates(dict(a=lambda: 1)), dict(a=1))

    def test_resolve_config_str(self):
        with patch('hod.config.config._resolve_templates', side_effect=lambda *args:dict(hostname=1)):
            self.assertEqual(hcc.resolve_config_str('abc'), 'abc')
            self.assertEqual(hcc.resolve_config_str('$hostname'), '1')
        with patch('hod.config.config._current_user', side_effect=lambda:'whoami'):
            with patch('os.getpid', side_effect=lambda: 1):
                with patch('os.getenv', side_effect=lambda *args:'/TMPDIR'):
                    with patch('socket.getfqdn', side_effect=lambda: 'hostname'):
                        self.assertEqual(hcc.resolve_config_str('$configdir'), '/TMPDIR/hod/whoami.hostname.1/conf') 
                        self.assertEqual(hcc.resolve_config_str('$workdir'), '/TMPDIR/hod/whoami.hostname.1/work')
    def test_ConfigOpts(self):
        config = StringIO("""
[Unit]
Name=testconfig
RunsOn=master

[Service]
ExecStart=starter
ExecStop=stopper

[Environment]
SOME_ENV=123""")
        cfg = hcc.ConfigOpts(config)
        self.assertEqual(cfg.name, 'testconfig')
        self.assertEqual(cfg.runs_on_master, True)
        self.assertEqual(cfg.start_script, 'starter')
        self.assertEqual(cfg.stop_script, 'stopper')
        self.assertTrue('SOME_ENV' in cfg.env)
        self.assertEqual(cfg.env['SOME_ENV'], '123')
        self.assertTrue(isinstance(cfg.env['SOME_ENV'], basestring))
        self.assertEqual(cfg.envstr(), 'SOME_ENV=123 ')

    def test_parse_runs_on(self):
        self.assertTrue(hcc._parse_runs_on('masTeR'))
        self.assertFalse(hcc._parse_runs_on('slavE'))
        self.assertRaises(RuntimeError, hcc._parse_runs_on, 'masterAndsLave')

    def test_parse_comma_delim_list(self):
        lst = hcc._parse_comma_delim_list('hello,world, have, a , nice,day')
        expect = ['hello', 'world', 'have', 'a', 'nice', 'day']
        self.assertEqual(lst, expect)
