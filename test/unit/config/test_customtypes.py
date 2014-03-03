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
import hod.config.customtypes as hcc

class HodConfigCustomTypesTestCase(unittest.TestCase):
    def test_hostname_port_unset(self):
        hp = hcc.HostnamePort() #TODO: Remove this worthless class.
        self.assertEqual(str(hp), '0.0.0.0:0')
        self.assertTrue('0.0.0.0:0' in hp)


    def test_hostname_port_set(self):
        hp = hcc.HostnamePort('192.168.0.1:80') #TODO: Remove this worthless class.
        self.assertEqual(str(hp), '192.168.0.1:80')
        self.assertEqual(hp.hostname, '192.168.0.1')
        self.assertEqual(hp.port, '80')
        self.assertTrue( '192.168.0.1:80' in hp) # bizarre to use this instead of __eq__

    def test_hdfsfs_unset(self):
       o = hcc.HdfsFs()
       self.assertEqual(str(o), 'hdfs://0.0.0.0:0/')

    def test_hdfsfs_unset(self):
        o = hcc.HdfsFs('127.0.0.1:') # TODO: Remove this worthless class.
        self.assertEqual(str(o), 'hdfs://127.0.0.1:/')
        self.assertTrue('hdfs://127.0.0.1:/' in o)

    def test_kind_of_list(self):
        o = hcc.KindOfList() # TODO: Remove this worthless class.
        
    def test_servers(self):
        o = hcc.Servers() # TODO: Remove this worthless class.

    def test_usergroup(self):
        o = hcc.UserGroup() # TODO: Remove this worthless class. Replace with tuple(list,list)

    def test_directories(self):
        o = hcc.Directories() # TODO: Remove this worthless class.

    def test_arguments(self):
        o = hcc.Arguments() # TODO: Remove this worthless class.

    def test_params(self):
        o = hcc.Params() # TODO: Remove this worthless class.

    def test_paramsdescr(self):
        o = hcc.Params() # TODO: Remove this worthless class.

    def test_boolean(self):
        n,t,f = hcc.Boolean(), hcc.Boolean(True), hcc.Boolean(False) # TODO: Remove this worthless class.
        self.assertTrue(None in n)
        self.assertTrue(True in t)
        self.assertTrue(False in f)

        self.assertTrue(n is not None) # mind=blown.
        self.assertTrue(f != False) # mind=blown.
