#!/usr/bin/env python
# ##
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
"""
hod-genconfig - parse a hod configuration file and output the resulting config
directory.

@author: Ewan Higgs (Ghent University)
"""

from textwrap import dedent

from hod.applications.application import Application
from vsc.utils import fancylogger
_log = fancylogger.getLogger(fname=False)

from hod.config.hodoption import HodOption
from hod.hodproc import ConfiguredMaster
from hod.mpiservice import setup_tasks

class GenConfigApplication(Application):
    def usage(self):
        s ="""\
        hod genconfig - Write hod configs to a directory for diagnostic purposes.
        hod genconfig --config-config=<hod.conf file> --config-workdir=<working directory>
        """
        return dedent(s)


    def run(self, args):
        options = HodOption(go_args=args)
        svc = ConfiguredMaster(options)
        try:
            setup_tasks(svc)
        except Exception as e:
            _log.error("Failed to setup hod tasks: %s", str(e))
            _log.exception("hod-genconfig failed")
