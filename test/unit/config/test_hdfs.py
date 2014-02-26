import unittest
import hod.config.hdfs as hch

class HodConfigHDFSTestCase(unittest.TestCase):
    def test_hdfscfg_init(self):
        cfg = hch.HdfsCfg()
        assert cfg.name == 'dfs' # TODO: should this be hdfs?

    def test_hdfsopts_init(self):
        cfg = hch.HdfsOpts()
        cfg.init_defaults()

    def test_hdfsopts_init_security_defaults(self):
        cfg = hch.HdfsOpts()
        cfg.init_security_defaults()

