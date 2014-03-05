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
import hod.config.client as hcc

class HodConfigClient(unittest.TestCase):
    '''Test CleintCfg functions'''

    def test_client_cfg(self):
        '''test client cfg'''
        o = hcc.ClientCfg()
        self.assertEqual(o.name, 'localclient')
        self.assertEqual(o.environment_script, None)

    def test_local_client_opts_init(self):
        '''test client opts init'''
        o = hcc.LocalClientOpts()
        o.init_defaults() # wait, didn't we just init?
        o.init_core_defaults_shared({})

    @unittest.expectedFailure
    def test_local_client_opts_gen_environment_script(self):
        '''test local client opts gen_environtment_script'''
        o = hcc.LocalClientOpts()
        o.gen_environment_script()
