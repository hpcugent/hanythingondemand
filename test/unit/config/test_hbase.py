import unittest
import hod.config.hbase as hch

class HodConfigHBase(unittest.TestCase):
    def test_hbasecfg_init(self):
        cfg = hch.HbaseCfg()
        assert cfg.daemonname == 'hbase'

    @unittest.expectedFailure
    def test_hbasecfg_basic_cfg_extra(self):
        cfg = hch.HbaseCfg()
        cfg.basic_cfg_extra()

    @unittest.expectedFailure
    def test_hbasecfg_which_hbase(self):
        cfg = hch.HbaseCfg()
        cfg.which_hbase()
        assert cfg.hbase is not None
        assert cfg.hbasehome is not None

    def test_hbasecfg_hbase_version(self):
        cfg = hch.HbaseCfg()
        cfg.hbase_version()

    def test_hbase_opts_init(self):
        cfg = hch.HbaseOpts()
        cfg.init_defaults()

    def test_hbaseopts_init_security_defaults(self):
        cfg = hch.HbaseOpts()
        cfg.init_security_defaults()

    @unittest.expectedFailure
    def test_hbaseopts_pre_run_any_service(self):
        cfg = hch.HbaseOpts()
        cfg.pre_run_any_service()
