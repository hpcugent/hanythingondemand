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
Generate a PBS job script using pbs_python. Will use mympirun to get the all started

@author: Stijn De Weirdt (Universiteit Gent)
@author: Ewan Higgs (Universiteit Gent)
"""
import os
import copy
import sys

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

import hod.cluster as hc
from hod import VERSION as HOD_VERSION
from hod.options import COMMON_HOD_CONFIG_OPTIONS, GENERAL_HOD_OPTIONS, RESOURCE_MANAGER_OPTIONS, validate_pbs_option
from hod.rmscheduler.hodjob import PbsHodJob
from hod.subcommands.subcommand import SubCommand


_log = fancylogger.getLogger('create', fname=False)


class CreateOptions(GeneralOption):
    """Option parser for 'create' subcommand."""
    VERSION = HOD_VERSION

    def resource_manager_options(self):
        """Add configuration options for job being submitted."""
        opts = copy.deepcopy(RESOURCE_MANAGER_OPTIONS)
        descr = ["Resource manager / Scheduler",
                 "Provide resource manager/scheduler related options (eg number of nodes)"]
        prefix = 'job'

        self.log.debug("Add resourcemanager option parser prefix %s descr %s opts %s", prefix, descr, opts)
        self.add_group_parser(opts, descr, prefix=prefix)

    def config_options(self):
        """Add general configuration options."""
        opts = copy.deepcopy(GENERAL_HOD_OPTIONS)
        opts.update(COMMON_HOD_CONFIG_OPTIONS)
        descr = ["Create configuration", "Configuration options for the 'create' subcommand"]

        self.log.debug("Add config option parser descr %s opts %s", descr, opts)
        self.add_group_parser(opts, descr)


class CreateSubCommand(SubCommand):
    """Implementation of 'create' subcommand."""
    CMD = 'create'
    EXAMPLE = "--hodconf=<hod.conf file> --workdir=<working directory>"
    HELP = "Submit a job to spawn a cluster on a PBS job controller"

    def run(self, args):
        """Run 'create' subcommand."""
        optparser = CreateOptions(go_args=args, envvar_prefix=self.envvar_prefix, usage=self.usage_txt)
        options = optparser.options
        if not validate_pbs_option(options):
            sys.stderr.write('Missing config options. Exiting.\n')
            return 1

        label = options.label

        if not hc.validate_label(label, hc.known_cluster_labels()):
            sys.exit(1)

        if not hc.validate_hodconf_or_dist(options.hodconf, options.dist):
            sys.exit(1)

        try:
            j = PbsHodJob(optparser)
            hc.report_cluster_submission(label)
            j.run()
            jobs = j.state()
            hc.post_job_submission(label, jobs, optparser.options.workdir)
            return 0
        except StandardError as err:
            fancylogger.setLogFormat(fancylogger.TEST_LOGGING_FORMAT)
            fancylogger.logToScreen(enable=True)
            _log.raiseException(err)
