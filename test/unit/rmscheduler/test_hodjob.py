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
import unittest
from cStringIO import StringIO
from mock import patch

import hod.rmscheduler.hodjob as hrh
from hod.rmscheduler.resourcemanagerscheduler import ResourceManagerScheduler
from hod.subcommands.create import CreateOptions
from hod.rmscheduler.rm_pbs import Pbs

manifest_config = """
[Meta]
version = 1
[Config]
workdir=/tmp
master_env= 
modules=
services=svc.conf
config_writer=some.module.function
directories=
"""

service_config = """
[Unit]
Name=wibble
RunsOn = master
[Service]
ExecStart=service start postgres
ExecStop=service stop postgres
[Environment]
"""

def _mock_open(name, *args):
    if name == 'hod.conf':
        return StringIO(manifest_config)
    else:
        return StringIO(service_config)


class HodRMSchedulerHodjobTestCase(unittest.TestCase):
    """Tests for HodJob class"""

    def setUp(self):
        '''setUp'''
        self.opt = CreateOptions(go_args=['progname', '--hodconf=hod.conf'])
        self.mpiopt = CreateOptions(go_args=['progname', '--hodconf=hod.conf'])

    def test_hodjob_init(self):
        '''test HodJob init function'''
        hj = hrh.HodJob(self.opt)

    def test_hodjob_set_type_class(self):
        '''test HodJob set_type_class'''
        hj = hrh.HodJob(self.opt)
        hj.set_type_class()
        self.assertEqual(hj.type_class, ResourceManagerScheduler)

    def test_hodjob_run(self):
        '''test HodJob run'''
        with patch('os.path.isfile', side_effect=lambda x: True):
            with patch('hod.rmscheduler.rm_pbs.Pbs.state', return_value=[]):
                hj = hrh.HodJob(self.opt)
                hj.run()

    def test_mympirunhod_init(self):
        '''test MympirunHod init functioon'''
        o = hrh.MympirunHod(self.opt)

    def test_mympirunhod_generate_exe(self):
        o = hrh.MympirunHod(self.mpiopt)
        exe = o.generate_exe()
        # not sure we want SNone/hod.output.SNone or a bunch of these defaults here.
        expected = ' '.join([
            'mympirun',
            '--output=$None/hod.output.$None',
            '--hybrid=1',
            '--variablesprefix=HOD',
            'python -m hod.local',
            '--hodconf=hod.conf',
        ])
        self.assertEqual(exe[0], expected)

    def test_pbshodjob_init(self):
        '''test pbshodjob init function'''
        os.environ['EBMODNAMEHANYTHINGONDEMAND'] = '/path/to/hanythindondemand'

        with patch('hod.rmscheduler.hodjob.resolve_config_paths', side_effect=['hod.conf']):
            with patch('__builtin__.open', side_effect=_mock_open):
                o = hrh.PbsHodJob(self.opt)

    def test_pbshodjob_set_type_class(self):
        '''test PbsHodJob set_type_class'''
        # should look into using mock or something here
        os.environ['EBMODNAMEHANYTHINGONDEMAND'] = '/path/to/hanythindondemand'
        with patch('hod.rmscheduler.hodjob.resolve_config_paths', side_effect=['hod.conf']):
            with patch('__builtin__.open', side_effect=_mock_open):
                o = hrh.PbsHodJob(self.mpiopt)
        o.set_type_class()
        self.assertEqual(o.type_class, Pbs)
