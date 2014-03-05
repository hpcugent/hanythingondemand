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
import unittest
import hod.config.hdfs as hch

class HodConfigHDFSTestCase(unittest.TestCase):
    '''Test the HdfsCfg class. Sadly we do not assert much here.'''
    def test_hdfscfg_init(self):
        '''test HdfsCfg init function'''
        cfg = hch.HdfsCfg()
        self.assertEqual(cfg.name, 'dfs') # TODO: should this be hdfs?

    def test_hdfsopts_init_defaults(self):
        '''test HdfsCfg init_defaults'''
        cfg = hch.HdfsOpts()
        cfg.init_defaults()

    def test_hdfsopts_init_security_defaults(self):
        '''test HdfsCfg init_security_defaults'''
        cfg = hch.HdfsOpts()
        cfg.init_security_defaults()
