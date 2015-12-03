##
# Copyright 2009-2015 Ghent University
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
Nothing here for now.

@author: Ewan Higgs (Ghent University)
"""

import unittest
from os.path import basename
from mock import patch, MagicMock

import hod.config.autogen.common as hcc
import hod.config.autogen.hadoop_on_lustre2 as hca

class TestConfigAutogenHadoopOnLustre(unittest.TestCase):
    def test_core_site_xml_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=4, totalcores=24, usablecores=[0, 1, 2, 3], num_nodes=1,
                memory=dict(meminfo=dict(memtotal=68719476736)))
        with patch('os.statvfs', return_value=MagicMock(f_bsize=4194304)):
            d = hca.core_site_xml_defaults('/', node)
        self.assertEqual(len(d), 8)
        self.assertEqual(d['fs.inmemory.size.mb'], 200)
        self.assertEqual(d['hadoop.tmp.dir'], '$workdir/tmp')
        self.assertEqual(d['io.file.buffer.size'],  4194304)
        self.assertEqual(d['io.sort.factor'], 64)
        self.assertEqual(d['io.sort.mb'], 256)

    def test_mapred_site_xml_defaults(self):
        '''Test mapred defaults; note: only using 4 from 24 cores.'''
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=4, totalcores=24, usablecores=[0, 1, 2, 3], num_nodes=1,
                memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        d = hca.mapred_site_xml_defaults('/', node)
        self.assertEqual(len(d), 9)
        self.assertEqual(d['hadoop.ln.cmd'], '/bin/ln')
        self.assertEqual(d['lustre.dir'], '$workdir')
        self.assertEqual(d['mapreduce.map.memory.mb'], hcc.round_mb(hcc.parse_memory('1G')))
        self.assertEqual(d['mapreduce.reduce.memory.mb'], hcc.round_mb(hcc.parse_memory('2G')))

    def test_yarn_site_xml_defaults(self):
        '''Test yarn defaults; note: only using 4 from 24 cores.'''
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=4, totalcores=24, usablecores=[0, 1, 2, 3], num_nodes=1,
                memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        d = hca.yarn_site_xml_defaults('/', node)
        self.assertEqual(len(d), 18)
        self.assertEqual(d['yarn.nodemanager.resource.memory-mb'], 9216)
        self.assertEqual(d['yarn.scheduler.minimum-allocation-mb'], 1024)
        self.assertEqual(d['yarn.scheduler.maximum-allocation-mb'], 9216)
        self.assertEqual(d['yarn.nodemanager.local-dirs'], '$workdir/$dataname')
        self.assertEqual(basename(d['yarn.nodemanager.local-dirs']), d['yarn.nodemanager.hostname'])

    def test_autogen_config(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, totalcores=24, usablecores=range(24), num_nodes=1,
                memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        with patch('os.statvfs', return_value=MagicMock(f_bsize=4194304)):
            d = hca.autogen_config('/', node)
        self.assertEqual(len(d), 4)
        self.assertTrue('core-site.xml' in d)
        self.assertTrue('mapred-site.xml' in d)
        self.assertTrue('yarn-site.xml' in d)
        self.assertTrue('capacity-scheduler.xml' in d)
