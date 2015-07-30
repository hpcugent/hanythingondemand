###
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
        self.assertTrue('scouter.yaml' in precfg.service_configs.keys())
        self.assertEqual(precfg.directories, ['/dfs/name', '/dfs/data'])
        self.assertEqual(hcc.invalid_fields(precfg), [])

    def test_PreServiceConfigOpts_kwargs(self):
        config = StringIO("""
[Meta]
version=1

[Config]
master_env=TMPDIR
modules=powerlevel/9001,scouter/1.0
services=scouter.conf
config_writer=hod.config.writer.scouter_yaml
directories=/dfs/name,/dfs/data

[scouter.yaml]
wibble=abc
wibble.class=super
        """)
        precfg = hcc.PreServiceConfigOpts(config, workdir='dbz-quotes',
                modules='dbz/episode-28')
        self.assertEqual(precfg.modules, ['powerlevel/9001', 'scouter/1.0',
            'dbz/episode-28'])
        for x in precfg.service_files:
            self.assertTrue(basename(x) in ['scouter.conf'])
        self.assertTrue('scouter.yaml' in precfg.service_configs.keys())
        self.assertEqual(precfg.directories, ['/dfs/name', '/dfs/data'])
        self.assertEqual(hcc.invalid_fields(precfg), [])
        self.assertEqual(precfg.workdir, 'dbz-quotes')

    def test_PreServiceConfigOpts_invalid(self):
        config = StringIO("""
[Meta]
version=

[Config]
master_env=TMPDIR
modules=powerlevel/9001,scouter/1.0
services=
workdir=
config_writer=hod.config.writer.scouter_yaml
directories=/dfs/name,/dfs/data

[scouter.yaml]
wibble=abc
wibble.class=super
        """)
        precfg = hcc.PreServiceConfigOpts(config)
        self.assertEqual(hcc.invalid_fields(precfg), ['version',
            'workdir', 'service_files'])

    def test_PreServiceConfigOpts_autogen_hadoop(self):
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
autogen=hadoop
        """)
        precfg = hcc.PreServiceConfigOpts(config)
        self.assertEqual(len(precfg.service_configs), 0)
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, totalcores=24, usablecores=range(24), topology=[0],
                memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        with patch('hod.node.node.Node.go', return_value=node):
            precfg.autogen_configs()
        self.assertEqual(len(precfg.service_configs), 4)
        self.assertTrue('core-site.xml' in precfg.service_configs)
        self.assertTrue('mapred-site.xml' in precfg.service_configs)
        self.assertTrue('yarn-site.xml' in precfg.service_configs)
        self.assertTrue('yarn.nodemanager.hostname' in precfg.service_configs['yarn-site.xml'])


    def test_PreServiceConfigOpts_autogen_hadoop_override(self):
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
autogen=hadoop

[yarn-site.xml]
yarn.nodemanager.hostname = 192.167.0.1
        """)
        precfg = hcc.PreServiceConfigOpts(config)
        self.assertEqual(len(precfg.service_configs), 1)
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, totalcores=24, usablecores=range(24), topology=[0],
                memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        with patch('hod.node.node.Node.go', return_value=node):
            precfg.autogen_configs()
        self.assertEqual(len(precfg.service_configs), 4)
        self.assertTrue('core-site.xml' in precfg.service_configs)
        self.assertTrue('mapred-site.xml' in precfg.service_configs)
        self.assertTrue('yarn-site.xml' in precfg.service_configs)
        yarncfg = precfg.service_configs['yarn-site.xml']
        self.assertTrue('yarn.nodemanager.hostname' in yarncfg)
        self.assertEqual(yarncfg['yarn.nodemanager.hostname'], '192.167.0.1')
        self.assertTrue('yarn.resourcemanager.hostname' in yarncfg)
        self.assertEqual(yarncfg['yarn.resourcemanager.hostname'], '$masterdataname')


    def test_PreServiceConfigOpts_merge(self):
        config1 = StringIO("""
[Meta]
version=1

[Config]
master_env=TMPDIR1
modules=powerlevel/9001,scouter/1.0
services=scouter.conf
workdir=/tmp
config_writer=hod.config.writer.scouter_yaml
directories=/dfs/name,/dfs/data

[scouter.yaml]
wibble=abc
wibble.class=super
    """)
        config2 = StringIO("""
[Meta]
version=1

[Config]
master_env=TMPDIR2
modules=Tackle/3.0,HydroPump/2.0
workdir=/tmp
config_writer=something_else
directories=/dfs/name,/dfs/data

[scouter.yaml]
wibble=abc
wibble.class=not-so-super

[other-service.yaml]
launch-code=1234
missile-type=tomahawk
    """)
        precfg1 = hcc.PreServiceConfigOpts(config1)
        precfg2 = hcc.PreServiceConfigOpts(config2)
        precfg = hcc.merge(precfg1, precfg2)
        self.assertEqual(precfg.master_env, precfg1.master_env + precfg2.master_env)
        self.assertEqual(precfg.modules, precfg1.modules + precfg2.modules)
        self.assertEqual(precfg.directories, precfg1.directories + precfg2.directories)
        self.assertEqual(precfg.workdir, precfg2.workdir)
        self.assertEqual(precfg.service_configs['scouter.yaml']['wibble.class'], 'not-so-super')
        self.assertEqual(precfg.service_configs['other-service.yaml']['launch-code'], '1234')

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
        self.assertEqual(hcc.env2str(cfg.env), 'SOME_ENV="123" ')

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
        self.assertRaises(KeyError, hcc._parse_runs_on, 'masterAndsLave')

    def test_parse_comma_delim_list(self):
        lst = hcc.parse_comma_delim_list('hello,world, have, a , nice,day')
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

    def test_ConfigOpts_ConfigParser_replacement(self):
        config = StringIO("""
[Unit]
Name=testconfig
RunsOn=master

[Service]
daemon=$$MYPATH
ExecStart=%(daemon)s/starter
ExecStop=%(daemon)s/stopper

[Environment]
SOME_ENV=123""")
        cfg = hcc.ConfigOpts(config, hct.TemplateResolver(workdir=''))
        self.assertEqual(cfg.start_script, '$MYPATH/starter')
        self.assertEqual(cfg.stop_script, '$MYPATH/stopper')

    def test_env2str(self):
        env = dict(PATH="/usr/bin", LD_LIBRARY_PATH="something with spaces")
        self.assertEqual(hcc.env2str(env), 'LD_LIBRARY_PATH="something with spaces" PATH="/usr/bin" ')


    def test_cfgget(self):
        config = StringIO("""
[Unit]
Name=testconfig
RunsOn=master

[Service]
daemon=$$MYPATH
ExecStart=%(daemon)s/starter
ExecStop=%(daemon)s/stopper

[Environment]
SOME_ENV=123""")
        cfg = hcc.load_service_config(config)
        self.assertEqual(hcc._cfgget(cfg, 'Service', 'daemon'), '$$MYPATH')
        self.assertEqual(hcc._cfgget(cfg, 'Service', 'daemon', 'default'), '$$MYPATH')
        self.assertEqual(hcc._cfgget(cfg, 'Service', 'daemon', 'default', daemon='override'), 'override')
        self.assertEqual(hcc._cfgget(cfg, 'Service', 'daemon2', 'notfound'), 'notfound')
        self.assertEqual(hcc._cfgget(cfg, 'Service', 'daemon2', 'notfound', daemon2='override'), 'override')


    def test_resolve_dist_path(self):
        with patch('sys.argv', ['/path/to/python/pkgs/bin/hod', '--dist=Program-1.2.3']):
            import sys
            print sys.argv[0]
            self.assertEqual(hcc.resolve_dist_path('Program-1.2.3'), '/path/to/python/pkgs/etc/hod/Program-1.2.3/hod.conf')

    def test_resolve_config_path(self):
        with patch('sys.argv', ['/path/to/python/pkgs/bin/hod', '--dist=Program-1.2.3']):
            import sys
            print sys.argv[0]
            self.assertEqual(hcc.resolve_config_paths('', 'Program-1.2.3'), '/path/to/python/pkgs/etc/hod/Program-1.2.3/hod.conf')
            self.assertEqual(hcc.resolve_config_paths('/path/to/python/pkgs/etc/hod/Program-1.2.3/hod.conf', ''),
                    '/path/to/python/pkgs/etc/hod/Program-1.2.3/hod.conf')
            self.assertRaises(RuntimeError, hcc.resolve_config_paths, '', '')
