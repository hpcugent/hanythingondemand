import unittest
import hod.work.hbase as hwh

class HodWorkHBaseTestCase(unittest.TestCase):
    def test_work_hbase_init(self):
        o = hwh.Hbase([0], {})

    def test_work_hbase_set_service_defaults(self):
        o = hwh.Hbase([0], {})
        o.set_service_defaults('mis') # TODO: what is 'mis'? A string, but what?

    def test_work_hbase_start_work_service_master(self):
        o = hwh.Hbase([0], {})
        #o.start_work_service_master()

    def test_work_hbase_start_work_service_slaves(self):
        o = hwh.Hbase([0], {})
        #o.start_work_service_slaves()

    @unittest.expectedFailure
    def test_work_hbase_stop_work_service_master(self):
        o = hwh.Hbase([0], {})
        o.stop_work_service_master()

    @unittest.expectedFailure
    def test_work_hbase_stop_work_service_slaves(self):
        o = hwh.Hbase([0], {})
        o.stop_work_service_slaves()
