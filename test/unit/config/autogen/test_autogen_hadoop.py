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
import hod.config.template as hct
import unittest
from mock import patch, MagicMock

class TestConfigAutogenHadoop(unittest.TestCase):
    def test_parse_memory(self):
        self.assertEqual(hca.parse_memory('1'), 1 * (1024**0))
        self.assertEqual(hca.parse_memory('1b'), 1 * (1024**0))
        self.assertEqual(hca.parse_memory('1B'), 1 * (1024**0))
        self.assertEqual(hca.parse_memory('2k'), 2 * (1024**1))
        self.assertEqual(hca.parse_memory('2kb'), 2 * (1024**1))
        self.assertEqual(hca.parse_memory('2kB'), 2 * (1024**1))
        self.assertEqual(hca.parse_memory('2KB'), 2 * (1024**1))
        self.assertEqual(hca.parse_memory('2K'), 2 * (1024**1))
        self.assertEqual(hca.parse_memory('3m'), 3 * (1024**2))
        self.assertEqual(hca.parse_memory('3M'), 3 * (1024**2))
        self.assertEqual(hca.parse_memory('4g'), 4 * (1024**3))
        self.assertEqual(hca.parse_memory('4G'), 4 * (1024**3))
        self.assertEqual(hca.parse_memory('5t'), 5 * (1024**4))
        self.assertEqual(hca.parse_memory('5T'), 5 * (1024**4))
        self.assertEqual(hca.parse_memory('5T'), 5 * (1024**4))

        self.assertEqual(hca.parse_memory('2.5G'), 2.5 * (1024**3))
        self.assertEqual(hca.parse_memory('0.5T'), 512 * (1024**3))

        self.assertRaises(RuntimeError, hca.parse_memory, '6p')
        self.assertRaises(RuntimeError, hca.parse_memory, '6P')

    def test_format_memory(self):
        self.assertEqual(hca.format_memory(1), '1b')
        self.assertEqual(hca.format_memory(1024), '1k')
        self.assertEqual(hca.format_memory(2000), '2000b')
        self.assertEqual(hca.format_memory(1024*1024), '1m')
        self.assertEqual(hca.format_memory(1024*1024, round_val=True), '1m')
        self.assertEqual(hca.format_memory(hca.parse_memory('0.5t')), '512g')
        self.assertEqual(hca.format_memory(hca.parse_memory('0.5t'), round_val=True), '512g')
        self.assertEqual(hca.format_memory(hca.parse_memory('8g')), '8g')
        self.assertEqual(hca.format_memory(hca.parse_memory('9t')), '9t')
        self.assertEqual(hca.format_memory(hca.parse_memory('7.5m')), '7680k')
        self.assertEqual(hca.format_memory(hca.parse_memory('7.5m'), round_val=True), '8m')
        # e.g. from our high memory machines
        self.assertEqual(hca.format_memory(540950507520, round_val=True), '504g')

    def test_reserved_memory(self):
        self.assertEqual(hca.reserved_memory(1024**0), hca.parse_memory('2g'))
        self.assertEqual(hca.reserved_memory(1024**1), hca.parse_memory('2g'))
        self.assertEqual(hca.reserved_memory(1024**2), hca.parse_memory('2g'))
        self.assertEqual(hca.reserved_memory(1024**2), hca.parse_memory('2g'))
        self.assertEqual(hca.reserved_memory(1024**3), hca.parse_memory('2g'))
        self.assertEqual(hca.reserved_memory(1024**4), hca.parse_memory('64g'))
        self.assertEqual(hca.reserved_memory(1024**5), hca.parse_memory('64g'))

    def test_set_default(self):
        x = dict(a=1, b=2)
        hca.set_default(x, 'c', 3)
        self.assertEqual(len(x), 3)
        hca.set_default(x, 'b', 4)
        self.assertEqual(x['b'], 2)
        hca.set_default(x, 'c', 4)
        self.assertEqual(x['c'], 3)

    def test_update_defaults(self):
        x = dict(a=1, b=2)
        hca.update_defaults(x, dict(a=0, b=0, c=0))
        self.assertEqual(len(x), 3)
        self.assertEqual(x['a'], 1)
        self.assertEqual(x['b'], 2)
        self.assertEqual(x['c'], 0)

    def test_min_container_size(self):
        pm = hca.parse_memory
        self.assertEqual(hca.min_container_size(hca.parse_memory('2g')), pm('256m'))
        self.assertEqual(hca.min_container_size(hca.parse_memory('4g')), pm('512m'))
        self.assertEqual(hca.min_container_size(hca.parse_memory('8g')), pm('1g'))
        self.assertEqual(hca.min_container_size(hca.parse_memory('16g')), pm('1g'))
        self.assertEqual(hca.min_container_size(hca.parse_memory('24g')), pm('2g'))

    def test_core_site_xml_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, usablecores=[0, 1, 2, 3], topology=[0],
                memory=dict(memtotal=68719476736))
        d = dict()
        with patch('os.statvfs', return_value=MagicMock(f_bsize=4194304)):
            d = hca.core_site_xml_defaults('/', node, d)
        self.assertEqual(len(d), 8)
        self.assertEqual(d['fs.inmemory.size.mb'], 200)
        self.assertEqual(d['io.file.buffer.size'],  4194304)
        self.assertEqual(d['io.sort.factor'], 64)
        self.assertEqual(d['io.sort.mb'], 256)

    def test_mapred_site_xml_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, usablecores=[0, 1, 2, 3], topology=[0],
                memory=dict(meminfo=dict(memtotal=68719476736)))
        d = dict()
        d = hca.mapred_site_xml_defaults('/', node, d)
        self.assertEqual(len(d), 6)
        self.assertEqual(d['mapreduce.map.memory.mb'], hca.parse_memory('8G') / (1024**2))
        self.assertEqual(d['mapreduce.reduce.memory.mb'], hca.parse_memory('16G') / (1024**2))

    def test_yarn_site_xml_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, usablecores=[0, 1, 2, 3], topology=[0],
                memory=dict(meminfo=dict(memtotal=68719476736)))
        d = dict()
        d = hca.yarn_site_xml_defaults('/', node, d)
        self.assertEqual(len(d), 9)
        self.assertEqual(d['yarn.nodemanager.resource.memory-mb'], hca.parse_memory('64G') / (1024**2))
        self.assertEqual(d['yarn.nodemanager.minimum-allocation-mb'], hca.parse_memory('8G') / (1024**2))
        self.assertEqual(d['yarn.nodemanager.maximum-allocation-mb'], hca.parse_memory('64G') / (1024**2))

    def test_capacity_scheduler_xml_defaults(self):
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, usablecores=[0, 1, 2, 3], topology=[0],
                memory=dict(meminfo=dict(memtotal=68719476736)))
        d = dict()
        d = hca.capacity_scheduler_xml_defaults('/', node, d)
        self.assertEqual(len(d), 3)
        self.assertEqual(d['yarn.scheduler.capacity.root.queues'], 'default')
        self.assertEqual(d['yarn.scheduler.capacity.root.default.capacity'], 100)
        self.assertEqual(d['yarn.scheduler.capacity.root.default.minimum-user-limit-percent'], 100)

    def test_autogen_config(self):
        d = {}
        with patch('os.statvfs', return_value=MagicMock(f_bsize=4194304)):
            d = hca.autogen_config('/', d)
        self.assertEqual(len(d), 4)
        self.assertTrue('core-site.xml' in d)
        self.assertTrue('mapred-site.xml' in d)
        self.assertTrue('yarn-site.xml' in d)
        self.assertTrue('capacity-scheduler.xml' in d)

    def test_autogen_config_update(self):
        d = {'core-site.xml': {}}
        with patch('os.statvfs', return_value=MagicMock(f_bsize=4194304)):
            d = hca.autogen_config('/', d)
        self.assertEqual(len(d), 4)
        self.assertTrue('core-site.xml' in d)
        self.assertTrue('mapred-site.xml' in d)
        self.assertTrue('yarn-site.xml' in d)
        self.assertTrue('capacity-scheduler.xml' in d)
