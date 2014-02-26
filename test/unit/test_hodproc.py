import unittest
from mock import sentinel
from optparse import OptionParser
from hod.config.hodoption import HodOption
import hod.hodproc as hh

class HodProcTestCase(unittest.TestCase):
    def test_slave_init_options_none(self):
        s = hh.Slave() 
        self.assertTrue(s.options is None)

    def test_slave_init_options_none(self):
        opts = sentinel.opts
        s = hh.Slave(opts)
        self.assertTrue( s.options == opts)

    def test_hadoop_master_init(self):
        opts = sentinel.opts
        hm = hh.HadoopMaster(opts)
        hm.options is not None

    def test_hadoop_master_distribution(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()

    def test_hadoop_master_make_client(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.make_client()

    def test_hadoop_master_distribution_hdfs(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.distribution_HDFS()
        self.assertTrue(hm.dists is not None)

    def test_hadoop_master_distribution_yarn(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.distribution_Yarn()
        self.assertTrue(hm.dists is not None)

    def test_hadoop_master_distribution_mapred(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.distribution_Mapred()
        self.assertTrue(hm.dists is not None)

    def test_hadoop_master_distribution_hbase(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        hm.distribution()
        hm.distribution_Hbase()
        self.assertTrue(hm.dists is not None)

    def test_hadoop_master_select_network(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        idx = hm.select_network()
        self.assertEqual(idx, 0)  #TODO: 5 line Function which just returns 0... remove.

    def test_hadoop_master_select_hdfs_ranks(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        ranks, allranks = hm.select_hdfs_ranks() # TODO: Remove convoluted nonsense.
        self.assertTrue(isinstance(ranks, int))
        self.assertTrue(isinstance(allranks, list))
        self.assertEqual(ranks, 0)
        self.assertEqual(allranks, range(hm.size))

    def test_hadoop_master_select_mapred_ranks(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts) 
        ranks, allranks = hm.select_mapred_ranks() # TODO: Remove convoluted nonsense.
        self.assertTrue(isinstance(ranks, int))
        self.assertTrue(isinstance(allranks, list))
        self.assertEqual(ranks, 0)
        self.assertEqual(allranks, range(hm.size))

    def test_hadoop_master_select_hbasemaster_ranks(self):
        opts = HodOption(go_args=['progname'])
        hm = hh.HadoopMaster(opts)
        ranks, allranks = hm.select_hbasemaster_ranks() # TODO: Remove convoluted nonsense.
        self.assertTrue(isinstance(ranks, int))
        self.assertTrue(isinstance(allranks, list))
        self.assertEqual(ranks, 0)
        self.assertEqual(allranks, range(hm.size))

