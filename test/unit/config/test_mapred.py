import unittest
import hod.config.mapred as hcm

class HodConfigMapred(unittest.TestCase):
    def test_mapredcfg_init(self):
        cfg = hcm.MapredCfg()
        assert cfg.name == 'mapred'

    def test_mapredopts_init(self):
        cfg = hcm.MapredOpts()
        cfg.init_defaults()

    def test_mapredopts_init_security_defaults(self):
        cfg = hcm.MapredOpts()
        cfg.init_security_defaults()

    def test_mapredopts_init_core_defaults_shared(self):
        cfg = hcm.MapredOpts()
        cfg.init_core_defaults_shared({})

    def test_mapredopts_check_hbase(self):
        cfg = hcm.MapredOpts()
        cfg.check_hbase()
