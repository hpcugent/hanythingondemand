
#
# Copyright 2012 Stijn De Weirdt
# 
# This file is part of HanythingOnDemand,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
from vsc import fancylogger
fancylogger.setLogLevelDebug()

import os, sys, re


class ResourceManagerScheduler:
    """Class to implement"""
    def __init__(self):
        self.log = fancylogger.getLogger(self.__class__.__name__)

        self.vars = {'cwd':None,
                     'jobid':None,
                     }
        self.jobid = None

        self.job_filter = None

    def submit(self, txt):
        """Submit the jobscript txt, set self.jobid"""
        self.log.error("submit not implemented")

    def state(self, jobid=None):
        """Return the state of job with id jobid"""
        if jobid is None:
            jobid = self.jobid
        self.log.error("state not implemented")

    def remove(self, jobid=None):
        """Remove the job with id jobid"""
        if jobid is None:
            jobid = self.jobid
        self.log.error("remove not implemented")

    def header(self, nodes=5, ppn= -1, walltime=72):
        """Return the script header that requests the properties.
           nodes = number of nodes
           ppn = ppn (-1 = full node)
           walltime = time in hours (can be float)
        """
        self.log.error("header not implemented")


