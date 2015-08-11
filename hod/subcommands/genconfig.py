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
hod genconfig - parse a hod configuration file and output the resulting config
directory.

@author: Ewan Higgs (Ghent University)
"""
import sys

from vsc.utils import fancylogger

from hod.hodproc import ConfiguredMaster
from hod.mpiservice import setup_tasks
from hod.subcommands.create import CreateOptions, validate_pbs_option
from hod.subcommands.subcommand import SubCommand


_log = fancylogger.getLogger('genconfig', fname=False)


class GenConfigSubCommand(SubCommand):
    """Implementation of 'genconfig' subcommand."""

    CMD = 'genconfig'
    EXAMPLE = "--config=<hod.conf file> --workdir=<working directory>"
    HELP = "Write hod configs to a directory for diagnostic purposes"

    def run(self, args):
        """Run 'genconfig' subcommand."""
        options = CreateOptions(go_args=args)
        if not validate_pbs_option(options):
            sys.stderr.write('Missing config options. Exiting.\n')
            sys.exit(1)

        svc = ConfiguredMaster(options)
        try:
            setup_tasks(svc)
        except Exception as e:
            _log.error("Failed to setup hod tasks: %s", str(e))
            _log.exception("hod-genconfig failed")
