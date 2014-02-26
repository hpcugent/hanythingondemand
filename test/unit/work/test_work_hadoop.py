import unittest
import hod.work.hadoop as hwh

class HodWorkHadopoTestCase(unittest.TestCase):
    def test_work_hadoop_init(self):
        o = hwh.Hadoop([0], {})

    def test_work_hadoop_interface_to_nn(self):
        o = hwh.Hadoop([0], {})
        o.interface_to_nn()

    def test_work_hadoop_prepare_extra_work_cfg(self):
        o = hwh.Hadoop([0], {})
        o.prepare_extra_work_cfg() # TODO: Remove

    def test_work_hadoop_prepare_work_cfg(self):
        o = hwh.Hadoop([0], {})
        o.prepare_work_cfg()

    @unittest.expectedFailure
    def test_work_hadoop_use_sdp(self):
        o = hwh.Hadoop([0], {})
        o.use_sdp()

    @unittest.expectedFailure
    def test_work_hadoop_use_sdp_java(self):
        o = hwh.Hadoop([0], {})
        o.use_sdp_java()

    @unittest.expectedFailure
    def test_work_hadoop_use_sdp_libsdp(self):
        o = hwh.Hadoop([0], {})
        o.use_sdp_libsdp('intf')
