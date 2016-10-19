# #
# Copyright 2009-2016 Ghent University
#
# This file is part of hanythingondemand
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/hanythingondemand
#
# hanythingondemand is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# hanythingondemand is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hanythingondemand. If not, see <http://www.gnu.org/licenses/>.
# #
"""
This module specifies the interface to implement for a ResourceNamagerScheduler

@author: Stijn De Weirdt (University of Ghent)
"""
from vsc.utils import fancylogger


class ResourceManagerScheduler(object):
    """Class to implement"""
    def __init__(self, options):
        self.log = fancylogger.getLogger(self.__class__.__name__, fname=False)

        self.vars = {
            'cwd': None,
            'jobid': None,
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

    def header(self, nodes=5, ppn=-1, walltime=72):
        """
        Return the script header that requests the properties.
        nodes = number of nodes
        ppn = ppn (-1 = full node)
        walltime = time in hours (can be float)
        """
        self.log.info("Using empty header (default implementation).")
        return ""
