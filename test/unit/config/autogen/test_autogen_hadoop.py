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

import hod.config.autogen.hadoop as hca
import hod.config.autogen.common as hcc
import hod.config.template as hct
import unittest
from mock import patch, MagicMock

class TestConfigAutogenHadoop(unittest.TestCase):
    def test_min_container_size(self):
        pm = hcc.parse_memory
        self.assertEqual(hca.min_container_size(pm('2g')), pm('256m'))
        self.assertEqual(hca.min_container_size(pm('4g')), pm('512m'))
        self.assertEqual(hca.min_container_size(pm('8g')), pm('1g'))
        self.assertEqual(hca.min_container_size(pm('16g')), pm('1g'))
        self.assertEqual(hca.min_container_size(pm('24g')), pm('2g'))

    def test_core_site_xml_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=4, totalcores=24, usablecores=[0, 1, 2, 3], num_nodes=1,
                memory=dict(meminfo=dict(memtotal=68719476736)))
        with patch('os.statvfs', return_value=MagicMock(f_bsize=4194304)):
            d = hca.core_site_xml_defaults('/', node)
        self.assertEqual(len(d), 8)
        self.assertEqual(d['fs.inmemory.size.mb'], 200)
        self.assertEqual(d['io.file.buffer.size'],  4194304)
        self.assertEqual(d['io.sort.factor'], 64)
        self.assertEqual(d['io.sort.mb'], 256)

    def test_mapred_site_xml_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, totalcores=24, usablecores=range(24), num_nodes=1,
                memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        d = hca.mapred_site_xml_defaults('/', node)
        self.assertEqual(len(d), 7)
        # Capped at 8g
        self.assertEqual(d['mapreduce.map.memory.mb'], hcc.round_mb(hcc.parse_memory('2G')))
        self.assertEqual(d['mapreduce.reduce.memory.mb'], hcc.round_mb(hcc.parse_memory('4G')))

    def test_yarn_site_xml_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, totalcores=24, usablecores=range(24), num_nodes=1,
                memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        d = hca.yarn_site_xml_defaults('/', node)
        self.assertEqual(len(d), 13)
        self.assertEqual(d['yarn.nodemanager.resource.memory-mb'], hcc.round_mb(hcc.parse_memory('56G')))
        self.assertEqual(d['yarn.resourcemanager.webapp.address'], '$masterhostaddress:8088')
        self.assertEqual(d['yarn.resourcemanager.webapp.https.address'], '$masterhostaddress:8090')
        self.assertEqual(d['yarn.nodemanager.hostname'], '$dataname')
        self.assertEqual(d['yarn.nodemanager.webapp.address'], '$hostaddress:8042')
        self.assertEqual(d['yarn.scheduler.minimum-allocation-mb'], hcc.round_mb(hcc.parse_memory('2G')))
        self.assertEqual(d['yarn.scheduler.maximum-allocation-mb'], hcc.round_mb(hcc.parse_memory('56G')))

    def test_capacity_scheduler_xml_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, totalcores=24, usablecores=range(24), num_nodes=1,
                memory=dict(meminfo=dict(memtotal=68719476736), ulimit='unlimited'))
        d = hca.capacity_scheduler_xml_defaults('/', node)
        self.assertEqual(len(d), 6)
        self.assertEqual(d['yarn.scheduler.capacity.root.queues'], 'default')
        self.assertEqual(d['yarn.scheduler.capacity.root.default.capacity'], 100)
        self.assertEqual(d['yarn.scheduler.capacity.root.default.minimum-user-limit-percent'], 100)
        self.assertEqual(d['yarn.scheduler.capacity.resource-calculator'], 
                'org.apache.hadoop.yarn.util.resource.DominantResourceCalculator')
        self.assertEqual(d['yarn.scheduler.capacity.root.default.acl_submit_applications'], '$user')
        self.assertEqual(d['yarn.scheduler.capacity.root.default.acl_administer_queue'], '$user')
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
