import unittest
import hod.rmscheduler.job as hrj

class HodRMSchedulerJobTestCase(unittest.TestCase):
    def test_job_init(self):
        j = hrj.Job(None)

    @unittest.expectedFailure
    def test_job_submit(self):
        j = hrj.Job(None)
        j.submit()

    @unittest.expectedFailure
    def test_job_generate_script(self):
        j = hrj.Job(None)
        j.generate_script()

    def test_job_generate_environment(self):
        j = hrj.Job(None)
        j.generate_environment()

    def test_job_generate_extra_environment(self):
        j = hrj.Job(None)
        j.generate_extra_environment()

    def test_job_generate_exe(self):
        j = hrj.Job(None)
        j.generate_exe()

    def test_job_generate_modules(self):
        j = hrj.Job(None)
        j.generate_modules()

    def test_job_get_jobs(self):
        hrj.Job.get_job(hrj.Job, None)

