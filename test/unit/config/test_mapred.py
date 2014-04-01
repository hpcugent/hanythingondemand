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
import hod.config.mapred as hcm

class HodConfigMapred(unittest.TestCase):
    '''Test the MapredCfg class. Sadly we do not assert much here.'''

    def test_mapredopts_init(self):
        '''test MapredCfg init_defaults'''
        cfg = hcm.MapredOpts()
        cfg.init_defaults()

    def test_mapredopts_init_security_defaults(self):
        '''test MapredCfg init_security_defaults'''
        cfg = hcm.MapredOpts()
        cfg.init_security_defaults()

    def test_mapredopts_init_core_defaults_shared(self):
        '''test MapredCfg init_core_defaults_shared'''
        cfg = hcm.MapredOpts()
        cfg.init_core_defaults_shared({})

    def test_mapredopts_check_hbase(self):
        '''test MapredCfg check_hbase'''
        cfg = hcm.MapredOpts()
        cfg.check_hbase()
