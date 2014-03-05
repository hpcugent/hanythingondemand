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
from mock import patch, sentinel
import os
from optparse import OptionParser, Values

import hod.rmscheduler.hodjob as hrh
import hod.config.hodoption as hch
from hod.rmscheduler.resourcemanagerscheduler import ResourceManagerScheduler
from hod.rmscheduler.hodjob import MympirunHodOption
from hod.rmscheduler.rm_pbs import Pbs


class HodRMSchedulerHodjobTestCase(unittest.TestCase):
    """Sadly there is a lot of mocking out here because get_hod is so reliant on
    the path scheme."""

    def setUp(self):
        '''setUp'''
        self.opt = hch.HodOption(go_args=['progname'])
        self.mpiopt = MympirunHodOption(go_args=['progname'])

    def test_hodjob_init(self):
        '''testt HodJob init function'''
        with patch('hod.rmscheduler.hodjob.HodJob.get_hod', side_effect=lambda: ('sentinel1', 'sentinel2')):
            hj = hrh.HodJob(self.opt)

    def test_hodjob_set_type_class(self):
        '''testt HodJob set_type_class'''
        with patch('hod.rmscheduler.hodjob.HodJob.get_hod', side_effect=lambda: ('sentinel1', 'sentinel2')):
            hj = hrh.HodJob(self.opt)
            hj.set_type_class()
        self.assertEqual(hj.type_class, ResourceManagerScheduler)

    def test_hodjob_get_hod(self):
        '''testt HodJob get_hod'''
        # TODO: Determine some tests for this path hacking 
        with patch('os.path.isfile', side_effect=lambda x: True):
            hj = hrh.HodJob(self.opt)
            hj.get_hod('hod_main')

    def test_hodjob_run(self):
        '''testt HodJob run'''
        with patch('os.path.isfile', side_effect=lambda x: True):
            hj = hrh.HodJob(self.opt)
            hj.run()

    def test_mympirunhod_init(self):
        '''test MympirunHod init functioon'''
        with patch('hod.rmscheduler.hodjob.HodJob.get_hod', side_effect=lambda: ('sentinel1', 'sentinel2')):
            o = hrh.MympirunHod(self.opt)

    def test_mympirunhod_generate_exe(self):
        with patch('hod.rmscheduler.hodjob.HodJob.get_hod', side_effect=lambda: ('sentinel1', 'sentinel2')):
            o = hrh.MympirunHod(self.mpiopt)
            exe = o.generate_exe()
        # not sure we want SNone/hod.output.SNone or a bunch of these defaults here.
        self.assertEqual(exe[0], 'mympirun --output=$None/hod.output.$None --hybrid=1 --variablesprefix=HADOOP,JAVA,HOD,MAPRED,HDFS,HDFS,MAPRED python sentinel1 --hod-envclass=MympirunHod')
        """ From prod:
        /usr/bin/python /apps/gent/SL6/sandybridge/software/vsc-mympirun/3.2.3/bin/mympirun --output=/vscmnt/gent_vulpix/_/user/home/gent/vsc410/vsc41041/jobs/hadoop/hod.output.12191.master16.delcatty.gent.vsc --hybrid=1 --variablesprefix=HADOOP,JAVA,HOD,MAPRED,HDFS,HDFS,MAPRED python /apps/gent/SL6/sandybridge/software/hanythingondemand/2.1.1-ictce-5.5.0-Python-2.7.6/bin/hod_main --hod-script=/user/home/gent/vsc410/vsc41041/jobs/hadoop/run_job.sh --hod-envclass=PbsEBMMHod
        """

    def test_easybuildmmhod_init(self):
        '''test EasybuildMMHod init function'''
        os.environ['EBMODNAMEHANYTHINGONDEMAND'] = '/path/to/hanythindondemand'

        with patch('hod.rmscheduler.hodjob.HodJob.get_hod', side_effect=lambda: ('sentinel1', 'sentinel2')):
            o = hrh.EasybuildMMHod(self.opt)

    def test_pbsebmmhod_init(self):
        '''test PbsEBMMHod init function'''
        os.environ['EBMODNAMEHANYTHINGONDEMAND'] = '/path/to/hanythindondemand'
        with patch('hod.rmscheduler.hodjob.HodJob.get_hod', side_effect=lambda: ('sentinel1', 'sentinel2')):
            o = hrh.PbsEBMMHod(self.mpiopt)

    def test_pbsebmmhod_set_type_class(self):
        '''test PbsEBMMHod set_type_class'''
        # should look into using mock or something here
        os.environ['EBMODNAMEHANYTHINGONDEMAND'] = '/path/to/hanythindondemand'
        o = hrh.PbsEBMMHod(self.mpiopt)
        o.set_type_class()
        self.assertEqual(o.type_class, Pbs)
