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
import unittest
import hod.rmscheduler.rm_pbs as hrr

class HodRMSchedulerRMPBSTestCase(unittest.TestCase):
    '''Test Pbs class functions'''

    def test_pbs_init(self):
        '''test Pbs init function'''
        o = hrr.Pbs(None)

    @unittest.expectedFailure
    def test_pbs_submit(self):
        '''test Pbs submit'''
        o = hrr.Pbs(None)
        o.submit()

    # this dumps core on localhost.
    #@unittest.expectedFailure
    #def test_pbs_state(self):
    #    o = hrr.Pbs(None)
    #    o.state()

    def test_pbs_info(self):
        '''test Pbs info -- though it doesn't do it yet.'''
        # TODO: Make this test the info function
        o = hrr.Pbs(None)

    def test_pbs_match_filter(self):
        '''test Pbs match_filter'''
        o = hrr.Pbs(None)
        o.match_filter('123') # TODO: cleanup use of 'filter'

    def test_pbs_remove(self):
        '''test Pbs remove'''
        o = hrr.Pbs(None)
        o.remove()

    @unittest.expectedFailure
    def test_pbs_header(self):
        '''test Pbs header'''
        o = hrr.Pbs(None)
        hdr = o.header()
        print hdr

    @unittest.expectedFailure
    def test_pbs_get_ppn(self):
        '''test Pbs get_ppn'''
        o = hrr.Pbs(None)
        o.get_ppn()
