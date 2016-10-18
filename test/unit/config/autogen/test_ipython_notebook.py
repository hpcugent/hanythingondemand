##
# Copyright 2009-2016 Ghent University
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
Tests for IPython Notebook autoconfiguration.

@author: Ewan Higgs (Ghent University)
"""

import hod.config.autogen.ipython_notebook as hcip
import hod.config.autogen.common as hcc

import unittest
class TestIpythonNodebook(unittest.TestCase):
    def test_spark_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                    cores=16, totalcores=16, usablecores=range(16), num_nodes=6,
                    memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        dflts = hcip.spark_defaults(None, node)
        self.assertTrue(len(dflts), 3)
        self.assertEqual(dflts['spark.executor.instances'], 47) # 6 nodes * 8 cores -1 core used for driver
        self.assertEqual(dflts['spark.executor.cores'], 2)
        self.assertEqual(hcc.parse_memory(dflts['spark.executor.memory']), hcc.parse_memory('7G'))

    def test_spark_defaults_single_node(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                    cores=16, totalcores=16, usablecores=range(16), num_nodes=1,
                    memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        dflts = hcip.spark_defaults(None, node)
        self.assertTrue(len(dflts), 3)
        self.assertEqual(dflts['spark.executor.instances'], 7)
        self.assertEqual(dflts['spark.executor.cores'], 2)
        self.assertEqual(hcc.parse_memory(dflts['spark.executor.memory']), hcc.parse_memory('7G'))

    def test_spark_defaults_single_core(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                    cores=1, totalcores=1, usablecores=range(1), num_nodes=1,
                    memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        dflts = hcip.spark_defaults(None, node)
        self.assertTrue(len(dflts), 3)
        self.assertEqual(dflts['spark.executor.instances'], 1)
        self.assertEqual(dflts['spark.executor.cores'], 1)
        self.assertEqual(hcc.parse_memory(dflts['spark.executor.memory']), hcc.parse_memory('56G'))
