#!/usr/bin/env python
# #
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
# #
"""
List available distributions known to hanythingondemand.

@author: Ewan Higgs (Ghent University)
@author: Kenneth Hoste (Ghent University)
"""
import sys
from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

from hod.config.config import avail_dists, load_service_config, resolve_dist_path
from hod.subcommands.subcommand import SubCommand


_log = fancylogger.getLogger('dists', fname=False)


class DistsSubCommand(SubCommand):
    """Implementation of HOD 'dists' subcommand."""
    CMD = 'dists'
    HELP = "List the available distributions"

    def run(self, args):
        """Run 'dists' subcommand."""
        lines = []
        dists = avail_dists()
        for dist in dists:
            modules = None
            try:
                cfg_fp = open(resolve_dist_path(dist))
                modules = load_service_config(cfg_fp).get('Config', 'modules').split(',')
                cfg_fp.close()
            except IOError as err:
                _log.error("Failed to get list of modules for dist '%s': %s", dist, err)
                continue

            lines.extend([
                "* %s" % dist,
                "    modules: %s" % ', '.join(modules),
                '',
            ])

        print '\n'.join(lines)
        return 0
