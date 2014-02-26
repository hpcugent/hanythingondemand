import unittest
import hod.config.client as hcc

class HodConfigClient(unittest.TestCase):
    def test_client_cfg(self):
        o = hcc.ClientCfg()
        assert o.name == 'localclient'
        assert o.environment_script == None

    def test_local_client_opts_init(self):
        o = hcc.LocalClientOpts()
        o.init_defaults() # wait, didn't we just init?
        o.init_core_defaults_shared({})
        print 'hello', o
        assert True

    @unittest.expectedFailure
    def test_local_client_opts_gen_environment_script(self):
        o = hcc.LocalClientOpts()
        o.gen_environment_script()
