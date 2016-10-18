#!/usr/bin/env python
# ##
# Copyright 2009-2016 Ghent University
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
import copy
import sys

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption


from hod import VERSION as HOD_VERSION
from hod.hodproc import ConfiguredMaster
from hod.mpiservice import setup_tasks
from hod.options import COMMON_HOD_CONFIG_OPTIONS, GENERAL_HOD_OPTIONS, validate_required_option
from hod.subcommands.subcommand import SubCommand
from hod.utils import setup_diagnostic_environment


_log = fancylogger.getLogger('genconfig', fname=False)


class GenConfigOptions(GeneralOption):
    """Option parser for 'genconfig' subcommand."""
    VERSION = HOD_VERSION

    def config_options(self):
        """Add general configuration options."""
        opts = copy.deepcopy(GENERAL_HOD_OPTIONS)
        opts.update(COMMON_HOD_CONFIG_OPTIONS)
        descr = ["Genconfig configuration", "Configuration options for the 'genconfig' subcommand"]

        self.log.debug("Add config option parser descr %s opts %s", descr, opts)
        self.add_group_parser(opts, descr)


class GenConfigSubCommand(SubCommand):
    """Implementation of 'genconfig' subcommand."""

    CMD = 'genconfig'
    EXAMPLE = "--hodconf=<hod.conf file> --workdir=<working directory>"
    HELP = "Write hod configs to a directory for diagnostic purposes"

    def run(self, args):
        """Run 'genconfig' subcommand."""

        setup_diagnostic_environment()

        optparser = GenConfigOptions(go_args=args, usage=self.usage_txt)
        if not validate_required_option(optparser.options):
            sys.stderr.write('Missing config options. Exiting.\n')
            return 1

        svc = ConfiguredMaster(optparser.options)
        try:
            setup_tasks(svc)
            return 0
        except Exception as e:
            _log.error("Failed to setup hod tasks: %s", str(e))
            _log.exception("hod genconfig failed")
            sys.exit(1)
