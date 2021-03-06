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
from mock import patch, Mock
from os.path import basename
from cStringIO import StringIO
from cPickle import dumps, loads

import hod.config.template as hct

class TestConfigTemplate(unittest.TestCase):
    def test_register_templates(self):
        reg = hct.TemplateRegistry()
        cfg = Mock(workdir='workdir', modules=['MyModule'])
        hct.register_templates(reg, cfg)
        self.assertEqual(reg.fields['masterhostname'].name, 'masterhostname')
        self.assertTrue(len(reg.fields['masterhostname'].doc) != 0)
        self.assertEqual(reg.fields['modules'].name, 'modules')
        self.assertEqual(reg.fields['modules'].fn(), 'MyModule')

    def test_register_templates_no_modules(self):
        reg = hct.TemplateRegistry()
        cfg = Mock(workdir='workdir', modules=[])
        hct.register_templates(reg, cfg)
        self.assertEqual(reg.fields['masterhostname'].name, 'masterhostname')
        self.assertTrue(len(reg.fields['masterhostname'].doc) != 0)
        self.assertEqual(reg.fields['modules'].fn(), '')

    def test_register_templates_multi_modules(self):
        reg = hct.TemplateRegistry()
        cfg = Mock(workdir='workdir', modules=['MyModule', 'MyOtherModule'])
        hct.register_templates(reg, cfg)
        self.assertEqual(reg.fields['masterhostname'].name, 'masterhostname')
        self.assertTrue(len(reg.fields['masterhostname'].doc) != 0)
        self.assertEqual(reg.fields['modules'].fn(), 'MyModule MyOtherModule')

    def test_TemplateRegistry(self):
        reg = hct.TemplateRegistry()
        reg.register(hct.ConfigTemplate('foo', lambda: 'wibble', 'A function'))
        self.assertTrue('foo' in reg.fields)
        self.assertEqual(reg.fields['foo'].name, 'foo')
        self.assertEqual(reg.fields['foo'].fn(), 'wibble')
        self.assertEqual(reg.fields['foo'].doc, 'A function')

    def test_resolve_config_str(self):
        self.assertEqual(hct.resolve_config_str('someval', **dict(configdir='someval')), 'someval')
        self.assertEqual(hct.resolve_config_str(47, **dict(configdir='someval')), 47)

    def test_localworkdir_no_jobid(self):
        with patch('hod.config.template._current_user', return_value='username'):
            with patch('os.getpid', return_value='123'):
                with patch('socket.getfqdn', return_value='hostname'):
                    with patch('os.getenv', return_value=None):
                        self.assertRaises(RuntimeError, hct.mklocalworkdir, 'workdir')

    def test_localworkdir_jobid(self):
        with patch('hod.config.template._current_user', return_value='username'):
            with patch('os.getpid', return_value='123'):
                with patch('socket.getfqdn', return_value='hostname'):
                    with patch('os.getenv', return_value='jobid'):
                        self.assertEqual('workdir/hod/jobid/username.hostname.123', hct.mklocalworkdir('workdir'))


    def test_TemplateResolver(self):
        with patch('hod.config.template.os.environ', dict(BINDIR='/usr/bin')):
            tr = hct.TemplateResolver(workdir='someval', greeting='hello')
            self.assertEqual(tr('$workdir $greeting joey joe joe',), 'someval hello joey joe joe')
            self.assertEqual(tr('$BINDIR/wibble'), '/usr/bin/wibble')
