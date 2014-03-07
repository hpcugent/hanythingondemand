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
import hod.config.hadoopcfg as hch

class HodConfigHadoopCfg(unittest.TestCase):
    '''Test HadoopCfg functions'''

    def test_hadoopcfg(self):
        '''Test the HadoopCfg class can create objects.'''
        cfg = hch.HadoopCfg()
        assert cfg.is_version_ok() is None
        assert cfg.is_version_ok('9001') is None

    def test_hadoopcfg_which_hadoop(self):
        '''Test the HadoopCfg which_hadoop function can find Hadoop.'''
        cfg = hch.HadoopCfg()
        assert cfg.hadoop is None
        assert cfg.hadoophome is None

        assert cfg.which_hadoop() is None

        assert cfg.hadoop is not None
        assert cfg.hadoophome is not None

    def test_hadoopcfg_java_version(self):
        '''Test the HadoopCfg can find the Java version.'''
        cfg = hch.HadoopCfg()
        self.assertEqual(len(cfg.javaversion), 3)
        self.assertEqual(cfg.javaversion['major'], -1)
        self.assertEqual(cfg.javaversion['minor'], -1 )
        self.assertTrue(cfg.javaversion['suffix'] is None)
        self.assertTrue(cfg.java_version() is None) # TODO: Move java version string manip to JavaVersion.
        self.assertEqual(cfg.javaversion['major'], 1)
        self.assertTrue(cfg.javaversion['minor'] > 4)
        self.assertTrue(cfg.javaversion['suffix'] > 4)

    @unittest.expectedFailure
    def test_hadoopcfg_locate_start_stop_daemon(self):
        '''Test the HadoopCfg can locate the start stop daemon.'''
        cfg = hch.HadoopCfg()
        cfg.locate_start_stop_daemon()
        self.assertTrue(cfg.start_script is not None)
        self.assertTrue(cfg.stop_script is not None)
        self.assertTrue(cfg.daemonname is 'hadoop')
