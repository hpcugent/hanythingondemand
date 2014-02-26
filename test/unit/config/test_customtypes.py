import unittest
import hod.config.customtypes as hcc

class HodConfigCustomTypesTestCase(unittest.TestCase):
    def test_hostname_port_unset(self):
        hp = hcc.HostnamePort() #TODO: Remove this worthless class.
        assert str(hp) == '0.0.0.0:0'
        assert '0.0.0.0:0' in hp 


    def test_hostname_port_set(self):
        hp = hcc.HostnamePort('192.168.0.1:80') #TODO: Remove this worthless class.
        assert str(hp) == '192.168.0.1:80'
        assert hp.hostname == '192.168.0.1'
        assert hp.port == '80'
        assert '192.168.0.1:80' in hp # bizarre to use this instead of __eq__

    def test_hdfsfs_unset(self):
       o = hcc.HdfsFs()
       assert str(o) == 'hdfs://0.0.0.0:0/'

    def test_hdfsfs_unset(self):
        o = hcc.HdfsFs('127.0.0.1:') # TODO: Remove this worthless class.
        assert str(o) == 'hdfs://127.0.0.1:/'
        assert 'hdfs://127.0.0.1:/' in o

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
        assert None in n
        assert True in t
        assert False in f

        assert n is not None # mind=blown.
        assert f != False # mind=blown.
