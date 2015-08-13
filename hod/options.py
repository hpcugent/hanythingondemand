#!/usr/bin/env python
# #
# Copyright 2009-2015 Ghent University
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
Hanythingondemand main program.

@author: Ewan Higgs (Universiteit Gent)
@author: Kenneth Hoste (Universiteit Gent)
"""
from vsc.utils.generaloption import GeneralOption

from hod import VERSION as HOD_VERSION


class HODOptions(GeneralOption):
    """Option parser for main 'hod' command."""
    VERSION = HOD_VERSION
    ALLOPTSMANDATORY = False  # allow more than one argument (e.g., a subcommand)

    def config_options(self):
        """Add configuration options."""
        opts = {
            'config': ("Top level configuration file. This can be "
                    "a comma separated list of config files with the later files taking "
                    "precendence.", "string", "store", ''),
            'dist': ("Prepackaged Hadoop distribution (e.g.  Hadoop/2.5.0-cdh5.3.1-native). "
                    "This cannot be set if config is set", "string", "store", ''),
            'workdir': ("Working directory", "string", "store", None),
        }
        descr = ["General configuration", "Configuration options that apply to different subcommands"]

        self.log.debug("Add config option parser descr %s opts %s", descr, opts)
        self.add_group_parser(opts, descr)
