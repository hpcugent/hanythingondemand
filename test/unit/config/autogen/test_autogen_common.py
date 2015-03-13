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

import hod.config.autogen.common as hcc
import unittest
from mock import patch, MagicMock
import errno

class TestConfigAutogenCommon(unittest.TestCase):
    def test_blocksize(self):
        with patch('os.statvfs', return_value=MagicMock(f_bsize=1024)):
            self.assertEqual(hcc.blocksize('/'), 1024) 
        with patch('os.statvfs', side_effect=OSError(errno.ENOENT, 'message')):
            self.assertRaises(OSError, hcc.blocksize, '/')
        with patch('os.statvfs', side_effect=OSError(errno.EACCES, 'message')):
            self.assertRaises(OSError, hcc.blocksize, '/')
        with patch('os.statvfs', side_effect=RuntimeError):
            self.assertRaises(RuntimeError, hcc.blocksize, '/')

        def fake_statvfs(path):
            if path == '/abc/def':
                raise OSError(errno.ENOENT, 'message')
            elif path == '/abc':
                return MagicMock(f_bsize=4096)
            else:
                raise OSError(errno.ENOENT, 'message')
        with patch('os.statvfs', side_effect=fake_statvfs):
            self.assertEqual(hcc.blocksize('/abc/def'), 4096)

    def test_reserved_memory(self):
        self.assertEqual(hcc.reserved_memory(1024**0), hcc.parse_memory('2g'))
        self.assertEqual(hcc.reserved_memory(1024**1), hcc.parse_memory('2g'))
        self.assertEqual(hcc.reserved_memory(1024**2), hcc.parse_memory('2g'))
        self.assertEqual(hcc.reserved_memory(1024**2), hcc.parse_memory('2g'))
        self.assertEqual(hcc.reserved_memory(1024**3), hcc.parse_memory('2g'))
        self.assertEqual(hcc.reserved_memory(1024**4), hcc.parse_memory('64g'))
        self.assertEqual(hcc.reserved_memory(1024**5), hcc.parse_memory('64g'))

    def test_parse_memory(self):
        self.assertEqual(hcc.parse_memory('1'), 1 * (1024**0))
        self.assertEqual(hcc.parse_memory('1b'), 1 * (1024**0))
        self.assertEqual(hcc.parse_memory('1B'), 1 * (1024**0))
        self.assertEqual(hcc.parse_memory('2k'), 2 * (1024**1))
        self.assertEqual(hcc.parse_memory('2kb'), 2 * (1024**1))
        self.assertEqual(hcc.parse_memory('2kB'), 2 * (1024**1))
        self.assertEqual(hcc.parse_memory('2KB'), 2 * (1024**1))
        self.assertEqual(hcc.parse_memory('2K'), 2 * (1024**1))
        self.assertEqual(hcc.parse_memory('3m'), 3 * (1024**2))
        self.assertEqual(hcc.parse_memory('3M'), 3 * (1024**2))
        self.assertEqual(hcc.parse_memory('4g'), 4 * (1024**3))
        self.assertEqual(hcc.parse_memory('4G'), 4 * (1024**3))
        self.assertEqual(hcc.parse_memory('5t'), 5 * (1024**4))
        self.assertEqual(hcc.parse_memory('5T'), 5 * (1024**4))
        self.assertEqual(hcc.parse_memory('5T'), 5 * (1024**4))

        self.assertEqual(hcc.parse_memory('2.5G'), 2.5 * (1024**3))
        self.assertEqual(hcc.parse_memory('0.5T'), 512 * (1024**3))

        self.assertRaises(RuntimeError, hcc.parse_memory, '6p')
        self.assertRaises(RuntimeError, hcc.parse_memory, '6P')

    def test_format_memory(self):
        pm = hcc.parse_memory
        self.assertEqual(hcc.format_memory(1), '1b')
        self.assertEqual(hcc.format_memory(1024), '1k')
        self.assertEqual(hcc.format_memory(2000), '2000b')
        self.assertEqual(hcc.format_memory(1024*1024), '1m')
        self.assertEqual(hcc.format_memory(1024*1024, round_val=True), '1m')
        self.assertEqual(hcc.format_memory(pm('0.5t')), '512g')
        self.assertEqual(hcc.format_memory(pm('0.5t'), round_val=True), '512g')
        self.assertEqual(hcc.format_memory(pm('8g')), '8g')
        self.assertEqual(hcc.format_memory(pm('9t')), '9t')
        self.assertEqual(hcc.format_memory(pm('7.5m')), '7680k')
        self.assertEqual(hcc.format_memory(pm('7.5m'), round_val=True), '8m')
        # e.g. from our high memory machines
        self.assertEqual(hcc.format_memory(540950507520, round_val=True), '504g')

    def test_set_default(self):
        x = dict(a=1, b=2)
        hcc.set_default(x, 'c', 3)
        self.assertEqual(len(x), 3)
        hcc.set_default(x, 'b', 4)
        self.assertEqual(x['b'], 2)
        hcc.set_default(x, 'c', 4)
        self.assertEqual(x['c'], 3)

    def test_update_defaults(self):
        x = dict(a=1, b=2)
        hcc.update_defaults(x, dict(a=0, b=0, c=0))
        self.assertEqual(len(x), 3)
        self.assertEqual(x['a'], 1)
        self.assertEqual(x['b'], 2)
        self.assertEqual(x['c'], 0)

    def test_round_mb(self):
        mb = 1024
        self.assertEqual(hcc.round_mb(512 * (1024**3)), 512 * mb)
        self.assertEqual(hcc.round_mb(64 * (1024**3)), 64 * mb)
        self.assertEqual(hcc.round_mb(32 * (1024**3)), 32 * mb)
        self.assertEqual(hcc.round_mb(32 * (1024**3) + 100*(1024**2)), 32 * mb)
        self.assertEqual(hcc.round_mb(32 * (1024**3) - 100*(1024**2)), 32 * mb - 1024)
        self.assertEqual(hcc.round_mb(16 * (1024**3)), 16 * mb)
        self.assertEqual(hcc.round_mb(8 * (1024**3)), 8 * mb)
        self.assertEqual(hcc.round_mb(4 * (1024**3)), 4 * mb)
        self.assertEqual(hcc.round_mb(3 * (1024**3)), 3 * mb)
        self.assertEqual(hcc.round_mb(2 * (1024**3)), 2 * mb)
        self.assertEqual(hcc.round_mb(1 * (1024**3)), 1 * mb)

    def test_cap(self):
        self.assertEqual(hcc.cap(10, 10), 10)
        self.assertEqual(hcc.cap(-10, 10), -10)
        self.assertEqual(hcc.cap(-10, 0), -10)
        self.assertEqual(hcc.cap(10, 0), 0)

    def test_available_memory_entire_machine(self):
        total_mem = 68719476736
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=24, totalcores=24, usablecores=range(24), topology=[0],
                memory=dict(meminfo=dict(memtotal=total_mem), ulimit='unlimited'))
        avail = total_mem - hcc.parse_memory('8g')
        self.assertEqual(hcc.available_memory(node), avail)

    def test_available_memory_ulimit(self):
        total_mem = 68719476736
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=8, totalcores=24, usablecores=range(24), topology=[0],
                memory=dict(meminfo=dict(memtotal=total_mem), ulimit='12345'))
        self.assertEqual(hcc.available_memory(node), 12345)

    def test_available_memory_one_third(self):
        total_mem = 68719476736
        node = dict(fqdn='hosty.domain.be', network='ib0', pid=1234,
                cores=8, totalcores=24, usablecores=range(24), topology=[0],
                memory=dict(meminfo=dict(memtotal=total_mem), ulimit='unlimited'))
        avail = total_mem - hcc.parse_memory('8g')
        self.assertEqual(hcc.available_memory(node), int(avail * 1./3))
        node['cores'] = 12
        self.assertEqual(hcc.available_memory(node), int(avail * 1./2))
        node['cores'] = 1 
        self.assertEqual(hcc.available_memory(node), int(avail * 1./24))
