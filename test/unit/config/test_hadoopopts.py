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
import os
from mock import patch
from xml.dom import minidom
import hod.config.hadoopopts as hch


class HodConfigHadoopOptsTestCase(unittest.TestCase):
    '''Test the HadoopOpts class. Sadly a lot of the functions are vvery
    side-effectful and difficult to test, so we are currently just checking that
    they can be called without crashing.'''
    @unittest.expectedFailure
    def test_hadoopopts_init_core_defaults_shared(self):
        '''test HadoopOpts core_ddefaults_shared.'''
        #TODO: Figure out how this function is supposed to work.
        cfg = hch.HadoopOpts()
        cfg.init_core_defaults_shared({'params': {'number': 42}, 'env_params': {'power_level': 9000}})
        self.assertTrue('params' in cfg.env_params)
        self.assertTrue('env_params' in cfg.env_params)
        self.assertTrue('wibble' in cfg.env_params)


    def test_hadoopopts_init_defaults(self):
        '''test HadoopOpts init_defaults'''
        cfg = hch.HadoopOpts()
        cfg.init_defaults() # TODO: Remove.

    def test_hadoopopts_set_defaults(self):
        '''test HadoopOpts set_defaults'''
        cfg = hch.HadoopOpts()
        cfg.set_defaults() # Waaaay too complicated for what it's doing.

    def test_hadoopopts_set_core_service_defaults(self):
        '''test HadoopOpts set_core_service_defaults'''
        cfg = hch.HadoopOpts()
        cfg.set_core_service_defaults('mis')
     
    def test_hadoopopts_basic_tuning(self):
        '''test HadoopOpts basic_tuning'''
        cfg = hch.HadoopOpts()
        cfg._basic_tuning()
        self.assertTrue('sort900' in cfg.tuning)
        self.assertTrue('sort1400' in cfg.tuning)

    def test_hadoopopts_create_xml_element(self):
        '''test HadoopOpts create_xml_element'''
        cfg = hch.HadoopOpts()
        doc = minidom.Document()
        cfg.create_xml_element(doc, 'wibble', '42', 'magic number')

    def test_hadoopopts_create_xml_element_final(self):
        '''test HadoopOpts create_xml_element final'''
        cfg = hch.HadoopOpts()
        doc = minidom.Document()
        cfg.create_xml_element(doc, 'wibble', '42', 'magic number', True)

    def test_hadoopopts_prep_dir(self):
        '''test HadoopOpts prep_dir'''
        cfg = hch.HadoopOpts()

    def test_hadoopopts_prep_conf_dir(self):
        '''test HadoopOpts prep_conf_dir'''
        cfg = hch.HadoopOpts()

    @unittest.expectedFailure
    def test_hadoopopts_gen_conf_xml_new(self):
        '''test HadoopOpts gen_conf_xml_new'''
        cfg = hch.HadoopOpts()
        cfg.gen_conf_xml_new()

    @unittest.expectedFailure
    def test_hadoopopts_gen_conf_env(self):
        '''test HadoopOpts gen_conf_env'''
        cfg = hch.HadoopOpts()
        cfg.gen_conf_env()

    @unittest.expectedFailure
    def test_hadoopopts_params_env_sanity_check(self):
        '''test HadoopOpts params_env_sanity_check'''
        cfg = hch.HadoopOpts()
        cfg.params_env_sanity_check()

    @unittest.expectedFailure
    def test_hadoopopts_pre_run_any_service(self):
        '''test HadoopOpts pre_run_any_service'''
        cfg = hch.HadoopOpts()
        cfg.pre_run_any_service()
        self.assertEqual(os.getenv('HADOOP_CONF_DIR'), cfg.confdir)

    def test_hadoopopts_set_niceness(self):
        '''test HadoopOpts set_niceness'''
        cfg = hch.HadoopOpts()
        with patch('hod.config.hadoopopts.which_exe',
                side_effect=lambda *args:''):
            cfg.set_niceness()

    def test_hadoopopts_set_niceness_hwloc(self):
        '''test HadoopOpts set_niceness with the hwlochindopts param'''
        cfg = hch.HadoopOpts()
        with patch('hod.config.hadoopopts.which_exe',
                side_effect=lambda *args:''):
            cfg.set_niceness(hwlocbindopts='')

    @unittest.expectedFailure
    def test_hadoopopts_make_opts_env_defaults(self):
        '''test HadoopOpts make_opts_env_defaults'''
        cfg = hch.HadoopOpts()
        cfg.make_opts_env_defaults()

    @unittest.expectedFailure
    def test_hadoopopts_make_opts_env_cfg(self):
        '''test HadoopOpts make_opts_env_cfg'''
        cfg = hch.HadoopOpts()
        cfg.make_opts_env_cfg()
