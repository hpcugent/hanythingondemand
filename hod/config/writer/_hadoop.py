# #
# Copyright 2009-2013 Ghent University
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
@author: Ewan Higgs
"""


def hadoop_xml(options, template_resolver):
    """Given a dict of options, write the resulting xml
    Params
    ------
    options : `dict`
    string key value pairs.

    template_resolver : `TemplateResolver`
    Resolver for template arguments.
    """
    output = """<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
"""
    for k, v in sorted(options.items()):
        name = template_resolver(k)
        value = template_resolver(v)
        output += """<property>
    <name>%s</name>
    <value>%s</value>
</property>
""" % (name, value)
    output += "</configuration>"
    return output
