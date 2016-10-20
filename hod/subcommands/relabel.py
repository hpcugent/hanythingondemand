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
Relabel a cluster.

@author: Ewan Higgs (Universiteit Gent)
"""

import sys

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

from hod import VERSION as HOD_VERSION
from hod.subcommands.subcommand import SubCommand
import hod.cluster as hc


_log = fancylogger.getLogger(fname=False)


class RelabelOptions(GeneralOption):
    """Option parser for 'relabel' subcommand."""
    VERSION = HOD_VERSION
    ALLOPTSMANDATORY = False # let us use optionless arguments.


class RelabelSubCommand(SubCommand):
    """Implementation of HOD 'relabel' subcommand."""
    CMD = 'relabel'
    EXAMPLE = "<source-cluster-label> <dest-cluster-label>"
    HELP = "Change the label of an existing job."

    def run(self, args):
        """Run 'relabel' subcommand."""
        optparser = RelabelOptions(go_args=args, envvar_prefix=self.envvar_prefix, usage=self.usage_txt)
        try:
            if len(optparser.args) != 3:
                _log.error(self.usage())
                sys.exit(1)

            labels = hc.known_cluster_labels()
            if optparser.args[1] not in labels:
                _log.error("Cluster with label '%s' not found", optparser.args[1])
                sys.exit(1)
            try:
                hc.mv_cluster_info(optparser.args[1], optparser.args[2])
            except (IOError, OSError) as err:
                _log.error("Could not change label '%s' to '%s': %s", optparser.args[1], optparser.args[2], err)
                sys.exit(1)
        except StandardError as err:
            fancylogger.setLogFormat(fancylogger.TEST_LOGGING_FORMAT)
            fancylogger.logToScreen(enable=True)
            _log.raiseException(err)
        return 0
