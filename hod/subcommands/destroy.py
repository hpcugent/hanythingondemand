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
Destroy an HOD cluster.

@author: Kenneth Hoste (Ghent University)
"""
import os
import sys

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

import hod
import hod.rmscheduler.rm_pbs as rm_pbs
from hod.cluster import cluster_info_exists, cluster_jobid, rm_cluster_info, rm_cluster_localworkdir
from hod.subcommands.subcommand import SubCommand


_log = fancylogger.getLogger('destroy', fname=False)


class DestroyOptions(GeneralOption):
    """Option parser for 'destroy' subcommand."""
    VERSION = hod.VERSION
    ALLOPTSMANDATORY = False # let us use optionless arguments.


class DestroySubCommand(SubCommand):
    """
    Implementation of HOD 'destroy' subcommand;
    destroys HOD cluster with specified label, regardless of cluster state, i.e.:
    * delete job (if it is still present)
    * remove hod.d directory corresponding to this cluster
    * remove local work directory used by this cluster
    """
    CMD = 'destroy'
    HELP = "Destroy an HOD cluster."
    EXAMPLE = "hod destroy <label>"

    def run(self, args):
        """Run 'destroy' subcommand."""
        optparser = DestroyOptions(go_args=args, envvar_prefix=self.envvar_prefix, usage=self.usage_txt)
        try:
            label, jobid = None, None

            if len(optparser.args) > 1:
                label = optparser.args[1]
                print "Destroying HOD cluster with label '%s'..." % label
            else:
                _log.error("No label provided.")
                sys.exit(1)

            try:
                jobid = cluster_jobid(label)
                print "Job ID: %s" % jobid
            except ValueError as err:
                _log.error(err)
                sys.exit(1)

            # try to figure out job state
            job_state = None

            pbs = rm_pbs.Pbs(optparser)
            jobs = pbs.state()
            pbsjobs = [job for job in jobs if job.jobid == jobid]
            _log.debug("Matching jobs for job ID '%s': %s", jobid, pbsjobs)

            if len(pbsjobs) == 1:
                job_state = pbsjobs[0].state 
                print "Job status: %s" % job_state

            elif len(pbsjobs) == 0:
                print "(job no longer found)"

            else:
                _log.error("Multiple jobs found with job ID '%s': %s", jobid, pbsjobs)
                sys.exit(1)

            # request confirmation is case the job is currently running
            if job_state == 'R':
                resp = raw_input("Confirm destroying the *running* HOD cluster with label '%s'? [y/n]: " % label)
                if resp != 'y':
                    print "(destruction aborted)"
                    return

            elif job_state in ['C', 'E']:
                print "(job has already ended/completed)"
                job_state = None

            print "\nStarting actual destruction of HOD cluster with label '%s'...\n" % label

            # actually destroy HOD cluster by deleting job and removing cluster info dir and local work dir
            if job_state is not None:
                # if job was not successfully deleted, pbs.remove will print an error message
                if pbs.remove(jobid):
                    print "Job with ID %s deleted." % jobid

            rm_cluster_localworkdir(label)

            if cluster_info_exists(label):
                rm_cluster_info(label)

            print "\nHOD cluster with label '%s' (job ID: %s) destroyed." % (label, jobid)

        except StandardError as err:
            fancylogger.setLogFormat(fancylogger.TEST_LOGGING_FORMAT)
            fancylogger.logToScreen(enable=True)
            _log.raiseException(err)
