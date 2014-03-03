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
import os
from xml.dom import minidom
import hod.config.hadoopopts as hch


class HodConfigHadoopOptsTestCase(unittest.TestCase):
    @unittest.expectedFailure
    def test_hadoopopts_init_core_defaults_shared(self):
        #TODO: Figure out how this function is supposed to work.
        cfg = hch.HadoopOpts()
        cfg.init_core_defaults_shared({'params': {'number': 42}, 'env_params': {'power_level': 9000}})
        print cfg.env_params
        assert 'params' in cfg.env_params
        assert 'env_params' in cfg.env_params
        assert 'wibble' in cfg.env_params


    def test_hadoopopts_init_core_defaults(self):
        cfg = hch.HadoopOpts()
        cfg.init_defaults() # TODO: Remove.

    def test_hadoopopts_set_defaults(self):
        cfg = hch.HadoopOpts()
        cfg.set_defaults() # Waaaay too complicated for what it's doing.

    def test_hadoopopts_set_core_service_defaults(self):
        cfg = hch.HadoopOpts()
        cfg.set_core_service_defaults('mis')
     
    def test_hadoopopts_basic_tuning(self):
        cfg = hch.HadoopOpts()
        cfg.basic_tuning()
        assert 'sort900' in cfg.tuning
        assert 'sort1400' in cfg.tuning

    def test_hadoopopts_create_xml_element(self):
        cfg = hch.HadoopOpts()
        doc = minidom.Document()
        cfg.create_xml_element(doc, 'wibble', '42', 'magic number')

    def test_hadoopopts_create_xml_element_final(self):
        cfg = hch.HadoopOpts()
        doc = minidom.Document()
        cfg.create_xml_element(doc, 'wibble', '42', 'magic number', True)

    def test_hadoopopts_prep_dir(self):
        cfg = hch.HadoopOpts()

    def test_hadoopopts_prep_conf_dir(self):
        cfg = hch.HadoopOpts()

    @unittest.expectedFailure
    def test_hadoopopts_gen_conf_xml_new(self):
        cfg = hch.HadoopOpts()
        #cfg.params_env_sanity_check()
        cfg.gen_conf_xml_new()

    @unittest.expectedFailure
    def test_hadoopopts_gen_conf_env(self):
        cfg = hch.HadoopOpts()
        cfg.gen_conf_env()

    @unittest.expectedFailure
    def test_hadoopopts_params_env_sanity_check(self):
        cfg = hch.HadoopOpts()
        cfg.params_env_sanity_check()

    @unittest.expectedFailure
    def test_hadoopopts_pre_run_any_service(self):
        cfg = hch.HadoopOpts()
        #cfg.prep_conf_dir()
        cfg.pre_run_any_service()
        assert os.getenv('HADOOP_CONF_DIR') == cfg.confdir

    def test_hadoopopts_set_niceness(self):
        cfg = hch.HadoopOpts()
        cfg.set_niceness()

    def test_hadoopopts_set_niceness_hwloc(self):
        cfg = hch.HadoopOpts()
        cfg.set_niceness(hwlocbindopts='')


    @unittest.expectedFailure
    def test_hadoopopts_make_opts_env_defaults(self):
        cfg = hch.HadoopOpts()
        cfg.make_opts_env_defaults()

    @unittest.expectedFailure
    def test_hadoopopts_make_opts_env_cfg(self):
        cfg = hch.HadoopOpts()
        cfg.make_opts_env_cfg()
