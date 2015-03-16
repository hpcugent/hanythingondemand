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

from StringIO import StringIO
from mock import patch
import copy
import socket
import unittest
import hod.node.node as hn

class HodNodeTestCase(unittest.TestCase):
    '''Test Node functions'''

    def test_netmask2maskbits(self):
        '''test netmask2maskbits'''
        self.assertEqual(0, hn.netmask2maskbits('0.0.0.0'))
        self.assertEqual(8, hn.netmask2maskbits('255.0.0.0'))
        self.assertEqual(16, hn.netmask2maskbits('255.255.0.0'))
        self.assertEqual(24, hn.netmask2maskbits('255.255.255.0'))
        self.assertEqual(25, hn.netmask2maskbits('255.255.255.128'))
        self.assertEqual(26, hn.netmask2maskbits('255.255.255.192'))
        self.assertEqual(27, hn.netmask2maskbits('255.255.255.224'))
        self.assertEqual(28, hn.netmask2maskbits('255.255.255.240'))
        self.assertEqual(29, hn.netmask2maskbits('255.255.255.248'))
        self.assertEqual(30, hn.netmask2maskbits('255.255.255.252'))
        self.assertEqual(31, hn.netmask2maskbits('255.255.255.254'))
        self.assertEqual(32, hn.netmask2maskbits('255.255.255.255'))

    def test_get_networks_single(self):
        '''
    $ ip addr show
    1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host
    valid_lft forever preferred_lft forever
    '''
        with patch('netifaces.interfaces', return_value=['lo']):
            with patch('netifaces.ifaddresses', return_value={2:[{'addr':'127.0.0.1', 'netmask':'255.0.0.0'}]}):
                with patch('socket.getfqdn', return_value='localhost'):
                    network = hn.get_networks()
                    self.assertEqual(network, [hn.NetworkInterface('localhost', '127.0.0.1', 'lo', 8)])

    def test_get_networks_multiple(self):
        '''
    $ ip addr show
    1: lo: --blah blah UP blah--
    link/loopback ---
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host
    valid_lft forever preferred_lft forever
    2: em1: --blah blah UP blah--
    link/ether ---
    inet 10.1.1.2/16 brd 255.255.255.128 scope global em1
    inet6 fe80::be30:5bff:fef7:7be8/64 scope link
    valid_lft forever preferred_lft forever
    3: em2: --blah blah DOWN blah--
    link/ether ---
    4: em3: --blah blah UP blah--
    link/ether ---
    inet 157.193.16.9/25 brd 157.193.16.127 scope global em3
    inet6 fe80::be30:5bff:fef7:7bec/64 scope link
    valid_lft forever preferred_lft forever
    5: em4: --blah blah DOWN blah--
    link/ether bc:30:5b:f7:7b:ed brd ff:ff:ff:ff:ff:ff
    6: ib0: --blah blah UP blah--
    link/infiniband ---
    inet 10.143.13.2/16 brd 10.143.255.255 scope global ib0
    inet6 fe80::202:c903:ea:98e1/64 scope link
    valid_lft ---
    7: em1.295@em1: --blah blah UP blah--
    link/ether bc: ---
    inet 172.24.13.2/16 brd 172.24.255.255 scope global em1.295
    inet6 fe80::be30:5bff:fef7:7be8/64 scope link
    valid_lft ---
    '''
        _interfaces = lambda: ['lo', 'em1', 'em2', 'em3', 'em4', 'ib0', 'em1.295@em1']
        _ifaddresses = lambda x: {
                'lo': {2:[{'addr':'127.0.0.1', 'netmask':'255.0.0.0'}]},
                'em1': {2:[{'addr':'10.1.1.2', 'netmask':'255.255.0.0'}]},
                'em2': {1:[{}]},
                'em3': {2:[{'addr':'157.193.16.9', 'netmask':'255.255.255.128'}]},
                'em4': {1:[]},
                'ib0': {2:[{'addr':'10.143.13.2', 'netmask':'255.255.0.0'}]},
                'em1.295@em1': {2:[{'addr':'172.24.13.2', 'netmask':'255.255.0.0'}]}
            }[x]
        _hostname = lambda x: {
                '127.0.0.1': 'localhost',
                '10.1.1.2': 'wibble01.wibble.os',
                '157.193.16.9': 'wibble01.sitename.tld',
                '10.143.13.2': 'wibble01.wibble.data',
                '172.24.13.2': 'wibble.sitename.nat'
            }[x]
        from hod.node.node import get_networks
        with patch('netifaces.interfaces', side_effect=_interfaces):
            with patch('netifaces.ifaddresses', side_effect=_ifaddresses):
                with patch('socket.getfqdn', side_effect=_hostname):
                    network = get_networks()
                    self.assertEqual(network, [
                            hn.NetworkInterface('localhost', '127.0.0.1', 'lo', 8),
                            hn.NetworkInterface('wibble01.wibble.os', '10.1.1.2', 'em1', 16),
                            hn.NetworkInterface('wibble01.sitename.tld', '157.193.16.9', 'em3', 25),
                            hn.NetworkInterface('wibble01.wibble.data', '10.143.13.2', 'ib0', 16),
                            hn.NetworkInterface('wibble.sitename.nat', '172.24.13.2', 'em1.295@em1', 16),
                            ])
    def test_address_in_network(self):
        '''test address in network'''
        self.assertTrue(hn.address_in_network('192.168.0.1', '192.168.0.0/24'))
        self.assertTrue(hn.address_in_network('192.169.2.3', '192.168.0.0/8'))
        self.assertFalse(hn.address_in_network('192.168.0.1', '10.0.0.0/24'))

    def test_ip_interface_to(self):
        '''test ip interface to'''
        networks = [
                hn.NetworkInterface('localhost', '127.0.0.1', 'lo', 8),
                hn.NetworkInterface('wibble01.wibble.os', '10.1.1.2', 'em1', 16),
                hn.NetworkInterface('wibble01.sitename.tld', '157.193.16.9', 'em3', 25),
                hn.NetworkInterface('wibble01.wibble.data', '10.143.13.2', 'ib0', 16),
                hn.NetworkInterface('wibble.sitename.nat', '172.24.13.2', 'em1.295@em1', 16),
                ]
        self.assertTrue(hn.ip_interface_to(networks, '192.168.0.1') is None)
        self.assertEqual(hn.ip_interface_to(networks, '127.9.10.11'), networks[0])
        self.assertEqual(hn.ip_interface_to(networks, '10.1.2.6'), networks[1])
        self.assertEqual(hn.ip_interface_to(networks, '157.193.16.10'), networks[2])
        self.assertTrue(hn.ip_interface_to(networks, '157.193.16.128') is None)

    def test_node_init(self):
        '''test node init'''
        n = hn.Node()
        self.assertEqual(n.fqdn, 'localhost')
        self.assertEqual(str(n), 'FQDN localhost PID -1')

    def test_node_go(self):
        '''test node go'''
        n = hn.Node()
        desc = n.go()
        self.assertTrue(desc is not None)

    def test_node_sorted_network_simple(self):
        '''test node order network'''
        nw = [hn.NetworkInterface('localhost', '127.0.0.1', 'lo', 8)]
        self.assertEqual(nw, hn.sorted_network(nw))


    def test_node_sorted_network_complex(self):
        '''test sorted_network puts IB before loopback'''
        nw = [hn.NetworkInterface('localhost', '127.0.0.1', 'lo', 8),
              hn.NetworkInterface('localhost', '127.0.0.1', 'ib3', 8)]
        sorted_nw = hn.sorted_network(copy.copy(nw))
        self.assertEqual([nw[1], nw[0]], sorted_nw)

    def test_sorted_networks_multiple_infiniband(self):
        '''
        We don't want to use infiniband interfaces that haven't had a
        hostname assigned to them.
        '''
        nw = [hn.NetworkInterface('localhost', '127.0.0.1', 'lo', 8),
              hn.NetworkInterface('wibble01.wibble.os', '10.1.1.2', 'em1', 16),
              hn.NetworkInterface('wibble01.sitename.tld', '157.193.16.9', 'em3', 25),
              hn.NetworkInterface('wibble01.wibble.data', '10.143.13.2', 'ib0', 16),
              hn.NetworkInterface('10.143.113.2', '10.143.113.2', 'ib1', 16)]
        sorted_nw = hn.sorted_network(copy.copy(nw))
        print sorted_nw
        self.assertEqual([nw[3], nw[2], nw[1], nw[4], nw[0]], sorted_nw)

    def test_node_get_memory_proc_meminfo(self):
        '''test node get memory'''
        meminfo = hn._get_memory_proc_meminfo()
        self.assertTrue(isinstance(meminfo, dict))
        self.assertTrue(len(meminfo) > 0)

    def test_node_ulimit_v(self):
        '''test node get memory'''
        ulimit = hn._get_memory_ulimit_v()
        print ulimit , type(ulimit)
        self.assertTrue(isinstance(ulimit, basestring))
        self.assertTrue(ulimit > 0)

    def test_node_get_memory(self):
        memory = hn.get_memory()
        self.assertTrue(isinstance(memory, dict))
        self.assertTrue('meminfo' in memory)
        self.assertTrue('ulimit' in memory)

    def test_node_get_totalcores(self):
        # NB: processor : 3 line has a tab in it.
        cpuinfo = StringIO('''
processor   : 0
vendor_id   : GenuineIntel
cpu family  : 6
processor   : 1
vendor_id   : GenuineIntel
cpu family  : 6
processor   : 2
vendor_id   : GenuineIntel
cpu family  : 6
processor	: 3
vendor_id   : GenuineIntel
cpu family  : 6
''')
        with patch('__builtin__.open', side_effect=lambda *args: cpuinfo):
            cores = hn.get_totalcores()
        self.assertEqual(cores, 4)
