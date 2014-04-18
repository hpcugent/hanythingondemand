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

@author: Stijn De Weirdt
"""
import os
import pwd
import tempfile
import re
import socket

from hod.node import ip_interface_to
from hod.work.work import Work

class Hadoop(Work):
    """Base Hadoop work class"""
    def __init__(self, options):
        Work.__init__(self)
        self.opts = options

    def prepare_extra_work_cfg(self):
        """Add some custom parameters"""

    def prepare_work_cfg(self):
        """prepare the config: collect the parameters and make the necessary xml cfg files"""
        self.opts.basic_cfg()
        if self.opts.basedir is None:
            self.opts.basedir = tempfile.mkdtemp(prefix='hod', suffix=".".join([
                pwd.getpwuid(os.getuid())[0],  # current user uid
                "%d" % self.rank,
                self.opts.name]
            ))

        self.prepare_extra_work_cfg()

        if None in self.opts.default_fsdefault:
            self.log.error("Primary nameserver still not set.")

        # # set the defaults
        self.opts.make_opts_env_defaults()

        # # make the cfg
        self.opts.make_opts_env_cfg()

        # # set the controldir to the confdir
        self.controldir = self.opts.confdir
