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
hod clone - copy a dist to a local directory for editing.

@author: Ewan Higgs (Ghent University)
"""
import os
import sys
import shutil

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption


import hod.config.config as hcc
from hod import VERSION as HOD_VERSION
from hod.subcommands.subcommand import SubCommand


_log = fancylogger.getLogger('clone', fname=False)


class CloneOptions(GeneralOption):
    """Option parser for 'clone' subcommand."""
    VERSION = HOD_VERSION
    ALLOPTSMANDATORY = False # let us use optionless arguments.


class CloneSubCommand(SubCommand):
    """Implementation of 'clone' subcommand."""

    CMD = 'clone'
    EXAMPLE = "<dist-to-copy> <output-directory>"
    HELP = "Write hod configs to a directory for editing purposes."

    def run(self, args):
        """Run 'clone' subcommand."""
        optparser = CloneOptions(go_args=args, usage=self.usage_txt)
        if len(optparser.args) < 3:
            sys.stderr.write(self.usage())
            sys.exit(1)

        dist = optparser.args[1]
        output_dir = optparser.args[2]

        if os.path.exists(output_dir):
            sys.stderr.write('Error: Output directory exists: "%s"\n' % output_dir)
            sys.exit(1)

        try:
            dists_dir = hcc.resolve_dists_dir()
            src = os.path.join(dists_dir, dist)
            if not os.path.exists(src):
                sys.stderr.write('Error: Input dist not found: "%s".\n' % dist)
                sys.exit(1)
            shutil.copytree(src, output_dir)
            return 0
        except Exception as err:
            _log.error("Failed to copy dist: %s", str(err))
            _log.exception("hod clone failed")
            sys.exit(1)
