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
from mock import sentinel
from optparse import OptionParser
from hod.config.hodoption import HodOption
import hod.hodproc as hh

class HodProcTestCase(unittest.TestCase):
    '''Test HodProc functions'''

    def test_rank_1(self):
        '''Test rank with size 1'''
        r, ar = hh._rank(1)
        self.assertEqual(r, 0)
        self.assertEqual(ar, range(1))

    def test_rank_5(self):
        '''Test rank with size 5'''
        r, ar = hh._rank(5)
        self.assertEqual(r, 0)
        self.assertEqual(ar, range(5))

    def test_hadoop_master_init(self):
        '''test hadoop master init'''
        opts = sentinel.opts
        hm = hh.HadoopMaster(opts)
        hm.options is not None

    def test_hadoop_master_distribution(self):
        '''test hadoop master distribution'''
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()

    def test_hadoop_master_make_client(self):
        '''test hadoop master make client'''
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.make_client()

    def test_hadoop_master_distribution_hdfs(self):
        '''test hadoop master distribution hdfs'''
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.distribution_HDFS()
        self.assertTrue(hm.dists is not None)

    def test_hadoop_master_distribution_yarn(self):
        '''test hadoop master distribution yarn'''
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.distribution_Yarn()
        self.assertTrue(hm.dists is not None)

    def test_hadoop_master_distribution_mapred(self):
        '''test hadoop master distribution mapred'''
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.distribution_Mapred()
        self.assertTrue(hm.dists is not None)

    def test_hadoop_master_distribution_hbase(self):
        '''test hadoop master distribution hbase'''
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.distribution_Hbase()
        self.assertTrue(hm.dists is not None)

    def test_hadoop_master_select_network(self):
        '''test hadoop master select network'''
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        idx = hm.select_network()
        self.assertEqual(idx, 0)  #TODO: 5 line Function which just returns 0... remove.
