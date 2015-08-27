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
Connect to a hod cluster.

@author: Ewan Higgs (Ghent University)
@author: Kenneth Hoste (Ghent University)
"""

import os
import os.path
import sys

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

from hod.local import cluster_env_file, cluster_jobid
from hod.subcommands.subcommand import SubCommand
import hod
import hod.rmscheduler.rm_pbs as rm_pbs


_log = fancylogger.getLogger(fname=False)

class ConnectOptions(GeneralOption):
    """Option parser for 'list' subcommand."""
    VERSION = hod.VERSION
    ALLOPTSMANDATORY = False # let us use optionless arguments.


class ConnectSubCommand(SubCommand):
    """
    Implementation of HOD 'connect' subcommand.
    Jobs must satisfy three constraints:
        1. Job must exist in the hod.d directory.
        2. The job must exist according to PBS.
        3. The job much be in running state.
    """
    CMD = 'connect'
    HELP = "Connect to a hod cluster."
    EXAMPLE = "hod connect <label>"

    def run(self, args):
        """Run 'connect' subcommand."""
        optparser = ConnectOptions(go_args=args, envvar_prefix=self.envvar_prefix, usage=self.usage_txt)
        try:
            if len(optparser.args) > 1:
                label = optparser.args[1]
            else:
                _log.error("No label provided.")
                sys.exit(1)

            try:
                jobid = cluster_jobid(label)
                env_script = cluster_env_file(label)
            except ValueError as e:
                _log.error(e.message)
                sys.exit(1)

            pbs = rm_pbs.Pbs(optparser)
            jobs = pbs.state()
            pbsjobs = [job for job in jobs if job.jid == label]

            if len(pbsjobs) == 0:
                _log.error("Job with job ID '%s' not found by pbs.", jobid)
                sys.exit(1)

            pbsjob = pbsjobs[0]
            if pbsjob.state == ['Q', 'H']:
                # This should never happen since the hod.d/<jobid>/env file is
                # written on cluster startup. Maybe someone hacked the dirs.
                _log.error("Cannot connect to cluster with job ID '%s' yet. It is still queued.", jobid)
                sys.exit(1)

            os.execvp('/usr/bin/ssh', ['ssh', '-t', pbsjob.ehosts, 'exec', 'bash', '--rcfile', env_script, '-i'])
            return 0 # pragma: no cover

        except StandardError as err:
            fancylogger.setLogFormat(fancylogger.TEST_LOGGING_FORMAT)
            fancylogger.logToScreen(enable=True)
            _log.raiseException(err.message)
