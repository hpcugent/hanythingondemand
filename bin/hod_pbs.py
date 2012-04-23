#!/usr/bin/env python
#
# Copyright 2012 Stijn De Weirdt
# 
# This file is part of HanythingOnDemand,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
"""
Generate a PBS job script using pbs_python. Will use mympirun to get the all started
"""

from hod.rmscheduler.hodjob import EasybuildPbsHod

if __name__ == '__main__':
    """Create the job script and submit it"""
    j = EasybuildPbsHod()
    j.run()
