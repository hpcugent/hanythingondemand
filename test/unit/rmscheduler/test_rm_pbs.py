import unittest
import hod.rmscheduler.rm_pbs as hrr

class HodRMSchedulerRMPBSTestCase(unittest.TestCase):
    def test_pbs_init(self):
        o = hrr.Pbs(None)

    @unittest.expectedFailure
    def test_pbs_submit(self):
        o = hrr.Pbs(None)
        o.submit()

    # this dumps core on localhost.
    #@unittest.expectedFailure
    #def test_pbs_state(self):
    #    o = hrr.Pbs(None)
    #    o.state()

    def test_pbs_info(self):
        o = hrr.Pbs(None)

    def test_pbs_match_filter(self):
        o = hrr.Pbs(None)
        o.match_filter('123') # TODO: cleanup use of 'filter'

    def test_pbs_remove(self):
        o = hrr.Pbs(None)
        o.remove()

    @unittest.expectedFailure
    def test_pbs_header(self):
        o = hrr.Pbs(None)
        hdr = o.header()
        print hdr

    @unittest.expectedFailure
    def test_pbs_get_ppn(self):
        o = hrr.Pbs(None)
        o.get_ppn()
