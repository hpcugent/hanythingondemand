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
import hod.config.hbase as hch

class HodConfigHBase(unittest.TestCase):
    def test_hbasecfg_init(self):
        '''test HbaseCfg init function'''
        cfg = hch.HbaseCfg()
        self.assertEqual(cfg.daemonname, 'hbase')

    @unittest.expectedFailure
    def test_hbasecfg_basic_cfg_extra(self):
        '''test HbaseCfg basic_cfg_extra'''
        cfg = hch.HbaseCfg()
        cfg.basic_cfg_extra()

    @unittest.expectedFailure
    def test_hbasecfg_which_hbase(self):
        '''test HbaseCfg which_hbase'''
        hbase, hbasehome = hch._which_hbase()
        self.assertTrue(hbase is not None)
        self.assertTrue(hbasehome is not None)

    def test_hbasecfg_hbase_version(self):
        '''test HbaseCfg which_hbase_version'''
        hbaseversion = hch._hbase_version()

    def test_hbase_opts_init(self):
        '''test HbaseCfg init_defaults'''
        cfg = hch.HbaseOpts()
        cfg.init_defaults()

    def test_hbaseopts_init_security_defaults(self):
        '''test HbaseCfg init_security_defaults'''
        cfg = hch.HbaseOpts()
        cfg.init_security_defaults()

    @unittest.expectedFailure
    def test_hbaseopts_pre_run_any_service(self):
        '''test HbaseCfg pre_run_any_service'''
        cfg = hch.HbaseOpts()
        cfg.pre_run_any_service()
