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
from mock import sentinel, patch
from cStringIO import StringIO
from optparse import OptionParser
from hod.config.hodoption import HodOption
import hod.hodproc as hh
from hod.config.template import TemplateResolver

class TestHodProcConfiguredMaster(unittest.TestCase):
    def test_configured_master_init(self):
        opts = HodOption(go_args=['progname'])
        self.assertTrue(hasattr(opts.options, 'config_config'))
        cm = hh.ConfiguredMaster(opts)

    def test_configured_master_distribution(self):
        manifest_config = StringIO("""
[Meta]
version = 1
[Config]
workdir=/tmp
master_env= 
modules=
services=svc.conf
config_writer=some.module.function
directories=
        """)
        service_config = StringIO("""
[Unit]
Name=wibble
RunsOn = master
[Service]
ExecStart=service start postgres
ExecStop=service stop postgres
[Environment]
        """)
        opts = HodOption(go_args=['progname', '--config-config', 'hod.conf'])
        cm = hh.ConfiguredMaster(opts)
        with patch('hod.hodproc._setup_config_paths', side_effect=lambda *args: None):
            with patch('__builtin__.open', side_effect=lambda name, *args: manifest_config if name == 'hod.conf' else service_config):
                cm.distribution()
        self.assertEqual(len(cm.tasks), 1)
