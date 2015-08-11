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

from hod.subcommands.subcommand import SubCommand
from hod.config.hodoption import HodOption
from hod.rmscheduler.hodjob import MympirunHodOption, PbsHodJob
from vsc.utils.generaloption import GeneralOption
from textwrap import dedent

from vsc.utils import fancylogger
_log = fancylogger.getLogger(fname=False)

def _validate_pbs_option(options):
    """pbs options require a config and a workdir"""
    if not options.options.config and not options.options.dist:
        _log.error('Either --config or --dist must be set')
        return False
    if options.options.config and options.options.dist:
        _log.error('Only one of --config or --dist can be set')
        return False
    if not options.options.workdir:
        _log.error('No workdir ("--workdir") provided')
        return False
    return True


class CreatePbsApplication(SubCommand):
    def usage(self):
        s ="""\
        hod pbs - Submit a job to spawn a cluster on a PBS job controller.
        hod pbs --config=<hod.conf file> --workdir=<working directory>
        """
        return dedent(s)

    def run(self, args):
        options = MympirunHodOption(go_args=args)
        if not _validate_pbs_option(options):
            raise ValueError('Missing config options')

        try:
            j = PbsHodJob(options)
            j.run()
        except StandardError as e:
            fancylogger.setLogFormat(fancylogger.TEST_LOGGING_FORMAT)
            fancylogger.logToScreen(enable=True)
            _log.raiseException(e.message)
