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
from os.path import basename
from cStringIO import StringIO
from cPickle import dumps, loads

import hod.config.config as hcc
import hod.config.template as hct

class HodConfigConfig(unittest.TestCase):
    '''Test Config functions'''

    def test_PreServiceConfigOpts(self):
        config = StringIO("""
[Meta]
version=1

[Config]
master_env=TMPDIR
modules=powerlevel/9001,scouter/1.0
services=scouter.conf
workdir=/tmp
config_writer=hod.config.writer.scouter_yaml
directories=/dfs/name,/dfs/data

[scouter.yaml]
wibble=abc
wibble.class=super
        """)
        precfg = hcc.PreServiceConfigOpts(config)
        self.assertEqual(precfg.modules, ['powerlevel/9001', 'scouter/1.0'])
        for x in precfg.service_files:
            self.assertTrue(basename(x) in ['scouter.conf'])
        print precfg.service_configs
        self.assertTrue('scouter.yaml' in precfg.service_configs.keys())
        self.assertEqual(precfg.directories, ['/dfs/name', '/dfs/data'])

    def test_ConfigOpts_runs_on_MASTER(self):
        config = StringIO("""
[Unit]
Name=testconfig
RunsOn=master

[Service]
ExecStart=starter
ExecStop=stopper

[Environment]
SOME_ENV=123""")
        cfg = hcc.ConfigOpts(config, hct.TemplateResolver(workdir=''))
        self.assertEqual(cfg.name, 'testconfig')
        self.assertEqual(cfg._runs_on, hcc.RUNS_ON_MASTER)
        self.assertEqual(cfg.runs_on(0, [0, 1, 2, 3]), [0])
        self.assertEqual(cfg.start_script, 'starter')
        self.assertEqual(cfg.stop_script, 'stopper')
        self.assertTrue('SOME_ENV' in cfg.env)
        self.assertEqual(cfg.env['SOME_ENV'], '123')
        self.assertTrue(isinstance(cfg.env['SOME_ENV'], basestring))
        self.assertEqual(hcc.env2str(cfg.env), 'SOME_ENV=123 ')

    def test_ConfigOpts_runs_on_SLAVE(self):
        config = StringIO("""
[Unit]
Name=testconfig
RunsOn=slave

[Service]
ExecStart=starter
ExecStop=stopper

[Environment]
SOME_ENV=123""")
        cfg = hcc.ConfigOpts(config, hct.TemplateResolver(workdir=''))
        self.assertEqual(cfg.name, 'testconfig')
        self.assertEqual(cfg._runs_on, hcc.RUNS_ON_SLAVE)
        self.assertEqual(cfg.runs_on(0, [0, 1, 2]), [1, 2])


    def test_ConfigOpts_runs_on_ALL(self):
        config = StringIO("""
[Unit]
Name=testconfig
RunsOn=all

[Service]
ExecStart=starter
ExecStop=stopper

[Environment]
SOME_ENV=123""")
        cfg = hcc.ConfigOpts(config, hct.TemplateResolver(workdir=''))
        self.assertEqual(cfg.name, 'testconfig')
        self.assertEqual(cfg._runs_on, hcc.RUNS_ON_ALL)
        self.assertEqual(cfg.runs_on(0, [0, 1, 2]), [0, 1, 2])

    def test_parse_runs_on(self):
        self.assertEqual(hcc._parse_runs_on('masTeR'), hcc.RUNS_ON_MASTER)
        self.assertEqual(hcc._parse_runs_on('slavE'), hcc.RUNS_ON_SLAVE)
        self.assertEqual(hcc._parse_runs_on('AlL'), hcc.RUNS_ON_ALL)
        self.assertRaises(ValueError, hcc._parse_runs_on, 'masterAndsLave')

    def test_parse_comma_delim_list(self):
        lst = hcc._parse_comma_delim_list('hello,world, have, a , nice,day')
        expect = ['hello', 'world', 'have', 'a', 'nice', 'day']
        self.assertEqual(lst, expect)

    def test_ConfigOpts_env(self):
        config = StringIO("""
[Unit]
Name=testconfig
RunsOn=master

[Service]
ExecStart=$BINDIR/starter
ExecStop=$BINDIR/stopper

[Environment]
SOME_ENV=123""")
        with patch('hod.config.template.os.environ', dict(BINDIR='/usr/bin')):
            cfg = hcc.ConfigOpts(config, hct.TemplateResolver(workdir=''))
            self.assertEqual(cfg.start_script, '/usr/bin/starter')
            self.assertEqual(cfg.stop_script, '/usr/bin/stopper')


    def test_ConfigOpts_pickles(self):
        config = StringIO("""
[Unit]
Name=testconfig
RunsOn=master

[Service]
ExecStart=starter
ExecStop=stopper

[Environment]
SOME_ENV=123""")
        cfg = hcc.ConfigOpts(config, hct.TemplateResolver(workdir=''))
        remade_cfg = loads(dumps(cfg))
        self.assertEqual(cfg.name, remade_cfg.name)
        self.assertEqual(cfg.start_script, remade_cfg.start_script)
        self.assertEqual(cfg.stop_script, remade_cfg.stop_script)
