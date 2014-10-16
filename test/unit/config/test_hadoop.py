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
from mock import patch 
from os.path import basename
from cStringIO import StringIO
from cPickle import dumps, loads

import hod.config.template as hct
import hod.config.writer as hcw

class HodConfigHadoop(unittest.TestCase):
    '''Test Config functions'''
    def test_hadoop_xml(self):
        tr = hct.TemplateResolver(somename="potato", workdir='')
        vals = {"fs.defaultFs": "file:///",
                "yarn.option.nested": "123",
                "templated.value": "$somename"
                }
        expected = """<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property>
    <name>fs.defaultFs</name>
    <value>file:///</value>
</property>
<property>
    <name>templated.value</name>
    <value>potato</value>
</property>
<property>
    <name>yarn.option.nested</name>
    <value>123</value>
</property>
</configuration>"""
        output = hcw.hadoop_xml('file.xml', vals, tr)
        print "\"%s\"" % expected
        print "\"%s\"" % output
        self.assertEqual(output, expected)

    def test_hadoop_xml_log4j_properties(self):
        tr = hct.TemplateResolver(somename="potato", workdir='')
        vals = {"fs.defaultFs": "file:///",
                "yarn.option.nested": "123",
                "templated.value": "$somename"
                }
        expected = """fs.defaultFs=file:///
templated.value=$somename
yarn.option.nested=123
"""
        output = hcw.hadoop_xml('file.properties', vals, tr)
        print "\"%s\"" % expected
        print "\"%s\"" % output
        self.assertEqual(output, expected)
