#!/usr/bin/env python

"""
Generate a PBS job script using pbs_python. Will use mympirun to get the all started
"""

from hod.rmscheduler.hodjob import EasybuildPbsHod

if __name__ == '__main__':
    """Create the job script and submit it"""
    j = EasybuildPbsHod()
    j.run()
