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

import os
import pytest
import unittest
from mock import patch, Mock
from collections import namedtuple

from ..util import capture
import hod.rmscheduler.rm_pbs as hrr


Attribs = namedtuple('attribs', 'name, attribs')
Attrib = namedtuple('attrib', 'name, value')

class HodRMSchedulerRMPBSTestCase(unittest.TestCase):
    '''Test Pbs class functions'''

    def test_master_hostname(self):
        fake_environ = os.environ.copy()
        fake_environ['PBS_DEFAULT'] = 'master123.test.gent.vsc'
        with patch('os.environ', fake_environ):
            self.assertTrue(hrr.master_hostname(), 'master123.test.gent.vsc')

    def test_pbs_init(self):
        '''test Pbs init function'''
        o = hrr.Pbs(None)

    def test_format_state_none(self):
        expected = 'No jobs found'
        self.assertTrue(expected, hrr.format_state([]))

    def test_format_state_single(self):
        job = hrr.PbsJob('123', 'R', 'host1')
        expected = 'Found 1 job Id 123 State R Node host1'
        self.assertTrue(expected, hrr.format_state([job]))

    def test_format_state_multiple(self):
        job1 = hrr.PbsJob('123', 'R', 'host1')
        job2 = hrr.PbsJob('abc', 'Q', '')
        expected = 'Found 2 jobs\n    Id 123 State R Node host1\n    Id abc State Q Node '
        self.assertTrue(expected, hrr.format_state([job1, job2]))

    def test_pbs_submit(self):
        '''test Pbs submit'''
        with patch('pbs.pbs_default'):
            with patch('pbs.pbs_connect'):
                with patch('pbs.pbs_submit', return_value=True):
                    o = hrr.Pbs(dict(name='test-job-name'))
                    o.get_ppn = lambda: 24
                    o.header()
                    o.submit('hostname')

    def test_pbs_state_none(self):
        statjob = []
        with patch('pbs.pbs_default'):
            with patch('pbs.pbs_connect'):
                with patch('pbs.pbs_statjob', return_value=statjob):
                    o = hrr.Pbs(None)
                    state = o.state()
        self.assertEqual(len(state), 0)

    def test_pbs_state_one(self):
        statjob = [Attribs(name='123.master.domain', attribs=[
                Attrib('job_state', 'R'),
                Attrib('exec_host', 'node1.domain/1+node1.domain/2'),
            ])
        ]
        with patch('pbs.pbs_default'):
            with patch('pbs.pbs_connect'):
                with patch('pbs.pbs_statjob', return_value=statjob):
                    o = hrr.Pbs(None)
                    state = o.state()
        self.assertEqual(len(state), 1)
        self.assertEqual(state[0].jobid, '123.master.domain')
        self.assertEqual(state[0].state, 'R')
        self.assertEqual(state[0].hosts, 'node1.domain')

    def test_pbs_info(self):
        '''test Pbs info -- though it doesn't do it yet.'''
        statjob = [Attribs(name='123.master.domain', attribs=[
                Attrib('Job_Name', 'HOD_job'),
                Attrib('job_state', 'R'),
                Attrib('exec_host', 'some-hosts'),
            ])
        ]
        expected = [{
            'id': '123.master.domain', 
            'Job_Name': 'HOD_job',
            'job_state': 'R', 
            'exec_host': 'some-hosts'
        }]
        with patch('pbs.pbs_default'):
            with patch('pbs.pbs_connect'):
                with patch('pbs.pbs_statjob', return_value=statjob):
                    o = hrr.Pbs(None)
                    info = o.info('123')
 
        self.assertEqual(info[0]['id'], expected[0]['id'])
        self.assertEqual(info[0]['Job_Name'], expected[0]['Job_Name'])
        self.assertEqual(info[0]['job_state'], expected[0]['job_state'])
        self.assertEqual(info[0]['exec_host'], expected[0]['exec_host'])
        self.assertEqual(info, expected)
 
    def test_pbs_match_filter(self):
        '''test Pbs match_filter'''
        job = {
            'id': '123.master.domain', 
            'Job_Name': 'HOD_job',
            'job_state': 'R', 
            'exec_host': 'some-hosts'
        }

        with patch('pbs.pbs_default'):
            with patch('pbs.pbs_connect'):
                o = hrr.Pbs(None)

        self.assertTrue(o.match_filter(job, {'Job_Name': '^HOD'}))
        self.assertFalse(o.match_filter(job, {'Job_Name': 'HOD$'}))

    def test_pbs_remove(self):
        '''
        test Pbs remove
        remove has no return value so we can't really assert anything
        interesting.
        '''
        with patch('pbs.pbs_default'):
            with patch('pbs.pbs_connect'):
                with patch('pbs.pbs_deljob', return_value=True):
                    o = hrr.Pbs(None)
                    o.remove()
                with patch('pbs.pbs_deljob', return_value=False):
                    o = hrr.Pbs(None)
                    o.remove()


    @pytest.mark.xfail
    def test_pbs_header(self):
        '''test Pbs header'''
        o = hrr.Pbs(None)
        hdr = o.header()

    def test_pbs_get_ppn_none(self):
        '''test Pbs get_ppn'''
        o = hrr.Pbs(None)
        nodes = { }

        with patch('PBSQuery.PBSQuery', return_value=Mock(getnodes=lambda: nodes)):
            self.assertTrue(o.get_ppn() is None)

    def test_pbs_get_ppn(self):
        '''test Pbs get_ppn'''
        o = hrr.Pbs(None)
        nodes = {
            'node1': {'np': ['24'], 'state': ['free']},
            'node2': {'np': ['24'], 'state': ['job-exclusive']}
        }

        with patch('PBSQuery.PBSQuery', return_value=Mock(getnodes=lambda: nodes)):
            self.assertEqual(24, o.get_ppn())
