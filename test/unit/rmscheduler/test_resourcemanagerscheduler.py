###
# Copyright 2009-2014 Ghent University
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
'''
@author Ewan Higgs (Universiteit Gent)
'''

import unittest
import hod.rmscheduler.resourcemanagerscheduler as hrr

class HodRMSchedulerResourceManagerSchedulerTestCase(unittest.TestCase):
    '''Test ResourceManagerSceduler functions'''

    def test_resourcemanagerscheduler_init(self):
        '''test ResourceManagerScheduler init function'''
        o = hrr.ResourceManagerScheduler(None)
        self.assertTrue('cwd' in o.vars)
        self.assertTrue('jobid' in o.vars)

    @unittest.expectedFailure
    def test_resourcemanagerscheduler_submit(self):
        '''test ResourceManagerScheduler submit'''
        o = hrr.ResourceManagerScheduler(None)
        o.submit() # TODO: Remove.

    def test_resourcemanagerscheduler_state(self):
        '''test ResourceManagerScheduler state'''
        o = hrr.ResourceManagerScheduler(None)
        o.state() # TODO: Remove.

    def test_resourcemanagerscheduler_remove(self):
        '''test ResourceManagerScheduler remove'''
        o = hrr.ResourceManagerScheduler(None)
        o.remove() # TODO: Remove.

    def test_resourcemanagerscheduler_header(self):
        '''test ResourceManagerScheduler header'''
        o = hrr.ResourceManagerScheduler(None)
        o.header() # TODO: Remove.
