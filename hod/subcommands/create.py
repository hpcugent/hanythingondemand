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
Generate a PBS job script using pbs_python. Will use mympirun to get the all started

@author: Stijn De Weirdt (Universiteit Gent)
@author: Ewan Higgs (Universiteit Gent)
"""
import copy
import sys

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

from hod import VERSION as HOD_VERSION
from hod.options import GENERAL_HOD_OPTIONS, validate_pbs_option
from hod.rmscheduler.hodjob import PbsHodJob
from hod.subcommands.subcommand import SubCommand


_log = fancylogger.getLogger('create', fname=False)


class CreateOptions(GeneralOption):
    """Option parser for 'create' subcommand."""
    VERSION = HOD_VERSION

    def resource_manager_options(self):
        """Add configuration options for job being submitted."""
        opts = {
            'walltime': ("Job walltime in hours", 'float', 'store', 48, 'l'),
            'nodes': ("Full nodes for the job", "int", "store", 5, "n"),
            'ppn': ("Processors per node (-1=full node)", "int", "store", -1),
            'mail': ("When to send mail (b=begin, e=end, a=abort)", "string", "extend", [], "m"),
            'mailothers': ("Other email adresses to send mail to", "string", "extend", [], "M"),
            'name': ("Job name", "string", "store", "HanythingOnDemand_job", "N"),
            'queue': ("Queue name (empty string is default queue)", "string", "store", "", "q"),
        }
        descr = ["Resource manager / Scheduler",
                 "Provide resource manager/scheduler related options (eg number of nodes)"]
        prefix = 'job'

        self.log.debug("Add resourcemanager option parser prefix %s descr %s opts %s", prefix, descr, opts)
        self.add_group_parser(opts, descr, prefix=prefix)

    def config_options(self):
        """Add general configuration options."""
        opts = copy.deepcopy(GENERAL_HOD_OPTIONS)
        opts.update({
            'label': ("Cluster label", 'string', 'store', None),
            'modules': ("Extra modules to load in each service environment", 'string', 'store', None),
        })
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
        options = CreateOptions(go_args=args, envvar_prefix=self.envvar_prefix, usage=self.usage_txt)
        if not validate_pbs_option(options):
            sys.stderr.write('Missing config options. Exiting.\n')
            return 1

        try:
            j = PbsHodJob(options)
            j.run()
        except StandardError as e:
            fancylogger.setLogFormat(fancylogger.TEST_LOGGING_FORMAT)
            fancylogger.logToScreen(enable=True)
            _log.raiseException(e.message)
