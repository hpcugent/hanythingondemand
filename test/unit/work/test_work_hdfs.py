import unittest
import hod.work.hdfs as hwh

class HodWorkHDFSTestCase(unittest.TestCase):
    def test_work_hdfs_init(self):
        o = hwh.Hdfs([0], {})

    def test_work_hdfs_set_service_defaults(self):
        o = hwh.Hdfs([0], {})
        o.set_service_defaults('mis') # TODO: what is 'mis'? A string, but what?

    def test_work_hdfs_start_work_service_master(self):
        o = hwh.Hdfs([0], {})
        #o.locate_start_stop_daemon()
        #o.start_work_service_master()

    def test_work_hdfs_start_work_service_slaves(self):
        o = hwh.Hdfs([0], {})
        #o.locate_start_stop_daemon()
        #o.start_work_service_slaves()

    def test_work_hdfs_stop_work_service_master(self):
        o = hwh.Hdfs([0], {})
        #o.locate_start_stop_daemon()
        #o.stop_work_service_master()

    def test_work_hdfse_stop_work_service_slaves(self):
        o = hwh.Hdfs([0], {})
        #o.locate_start_stop_daemon()
        #o.stop_work_service_slaves()
