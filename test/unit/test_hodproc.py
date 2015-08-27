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
from cStringIO import StringIO
import hod.hodproc as hh
from hod.subcommands.create import CreateOptions
from hod.config.template import TemplateResolver

manifest_config = """
[Meta]
version = 1
[Config]
workdir=/tmp
master_env= 
modules=
services=svc.conf
config_writer=some.module.function
directories=
"""

service_config = """
[Unit]
Name=wibble
RunsOn = master
[Service]
ExecStart=service start postgres
ExecStop=service stop postgres
[Environment]
"""

def _mock_open(name, *args):
    if name == 'hod.conf':
        return StringIO(manifest_config)
    else:
        return StringIO(service_config)

class TestHodProcConfiguredMaster(unittest.TestCase):
    def test_configured_master_init(self):
        opts = CreateOptions(go_args=['progname'])
        self.assertTrue(hasattr(opts.options, 'hodconf'))
        cm = hh.ConfiguredMaster(opts)
        self.assertEqual(cm.options, opts)

    def test_configured_master_distribution(self):
        opts = CreateOptions(go_args=['progname', '--hodconf', 'hod.conf',
        '--modules', 'Python-2.7.9-intel-2015a,Spark/1.3.0'])
        autogen_config = Mock()
        cm = hh.ConfiguredMaster(opts)
        with patch('hod.hodproc._setup_config_paths', side_effect=None):
            with patch('hod.config.config.PreServiceConfigOpts.autogen_configs',
                    side_effect=autogen_config):
                with patch('hod.hodproc.resolve_config_paths', side_effect=['hod.conf']):
                    with patch('__builtin__.open', side_effect=_mock_open):
                        cm.distribution()
        self.assertEqual(len(cm.tasks), 1)
        self.assertTrue(autogen_config.called)
        self.assertEqual(autogen_config.call_count, 1)
        self.assertTrue('Python-2.7.9-intel-2015a' in cm.tasks[0].config_opts.modules)
        self.assertTrue('Spark/1.3.0' in cm.tasks[0].config_opts.modules)

    def test_configured_slave_distribution(self):
        opts = CreateOptions(go_args=['progname', '--hodconf', 'hod.conf',
        '--modules', 'Python-2.7.9-intel-2015a,Spark/1.3.0'])
        autogen_config = Mock()
        cm = hh.ConfiguredSlave(opts)
        with patch('hod.hodproc._setup_config_paths', side_effect=None):
            with patch('hod.config.config.PreServiceConfigOpts.autogen_configs',
                    side_effect=autogen_config):
                with patch('hod.hodproc.resolve_config_paths', side_effect=['hod.conf']):
                    with patch('__builtin__.open', side_effect=_mock_open):
                        cm.distribution()
        self.assertTrue(cm.tasks is None) # slaves don't collect tasks.
        self.assertTrue(autogen_config.called)
        self.assertEqual(autogen_config.call_count, 1)
