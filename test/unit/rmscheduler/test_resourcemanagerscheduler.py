import unittest
import hod.rmscheduler.resourcemanagerscheduler as hrr

class HodRMSchedulerResourceManagerSchedulerTestCase(unittest.TestCase):
    def test_resourcemanagerscheduler_init(self):
        o = hrr.ResourceManagerScheduler(None)
        assert 'cwd' in o.vars 
        assert 'jobid' in o.vars 

    @unittest.expectedFailure
    def test_resourcemanagerscheduler_submit(self):
        o = hrr.ResourceManagerScheduler(None)
        o.submit() # TODO: Remove.

    def test_resourcemanagerscheduler_state(self):
        o = hrr.ResourceManagerScheduler(None)
        o.state() # TODO: Remove.

    def test_resourcemanagerscheduler_remove(self):
        o = hrr.ResourceManagerScheduler(None)
        o.remove() # TODO: Remove.

    def test_resourcemanagerscheduler_header(self):
        o = hrr.ResourceManagerScheduler(None)
        o.header() # TODO: Remove.
