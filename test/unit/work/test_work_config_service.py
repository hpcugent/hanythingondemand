##
# Copyright 2009-2013 Ghent University
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
##
"""
@author: Ewan Higgs
"""
import os
import unittest
from mock import patch, sentinel
from cStringIO import StringIO

import hod.work.config_service as hwc
import hod.config.config as hcc
import hod.config.template as hct

def _mk_master_config():
    return StringIO("""
[Unit]
Name=test
RunsOn=master
[Service]
ExecStart=echo hello
ExecStop=echo hello
[Environment]
    """)

def _mk_slave_config():
    return StringIO("""
[Unit]
Name=test
RunsOn=slave
[Service]
ExecStart=echo hello
ExecStop=echo hello
[Environment]
    """)

class TestHodWorkConfiguredService(unittest.TestCase):
    '''Test the ConfiguredService'''

    def test_ConfiguredService_init(self):
        '''Test creation of the ConfiguredService'''
        cfg = hcc.ConfigOpts.from_file(_mk_master_config(), hct.TemplateResolver(workdir='/tmp'))
        cs = hwc.ConfiguredService(cfg)

    def test_ConfiguredService_pre_start_work_service(self):
        '''Test ConfiguredService pre_start method'''
        cfg = hcc.ConfigOpts.from_file(_mk_master_config(), hct.TemplateResolver(workdir='/tmp'))
        cs = hwc.ConfiguredService(cfg)
        cs.pre_start_work_service()

    def test_ConfiguredService_start_work_service(self):
        '''Test ConfiguredService start method'''
        cfg = hcc.ConfigOpts.from_file(_mk_master_config(), hct.TemplateResolver(workdir='/tmp'))
        cs = hwc.ConfiguredService(cfg)
        cs.start_work_service()

    def test_ConfiguredService_stop_work_service(self):
        '''Test ConfiguredService stop method'''
        cfg = hcc.ConfigOpts.from_file(_mk_master_config(), hct.TemplateResolver(workdir='/tmp'))
        cs = hwc.ConfiguredService(cfg)
        cs.stop_work_service()

    def test_ConfiguredService_prepare_work_cfg(self):
        cfg = hcc.ConfigOpts.from_file(_mk_slave_config(), hct.TemplateResolver(workdir='/tmp'))
        cs = hwc.ConfiguredService(cfg)
        localworkdir = '/tmp/label.node1234.user.123'
        with patch('hod.work.config_service.os.makedirs', side_effect=lambda *args: None):
            with patch('hod.config.template.mklocalworkdir', side_effect=lambda *args, **kwargs: localworkdir):
                cs.prepare_work_cfg()
        self.assertEqual(cs.controldir, os.path.join(localworkdir, 'controldir'))
