import hod.work.client as hwc
import unittest

class HodWorkClientTestCasE(unittest.TestCase):
    def test_localclient_init(self):
        o = hwc.LocalClient([0], {})

    def test_localclient_start_work_service_master(self):
        o = hwc.LocalClient([0], {})
        #o.start_work_service_master()

    def test_localclient_stop_work_service_master(self):
        o = hwc.LocalClient([0], {})
        #o.stop_work_service_master()

    def test_remoteclient_init(self):
        o = hwc.RemoteClient([0], {})

    def test_remoteclient_start_work_service_master(self):
        o = hwc.RemoteClient([0], {})
        #o.start_work_service_master()

    def test_remoteclient_stop_work_service_master(self):
        o = hwc.RemoteClient([0], {})
        #o.start_work_service_master()
