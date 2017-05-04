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
Abstract base class for subcommand support.

@author: Ewan Higgs (Universiteit Gent)
"""
import sys
from abc import abstractmethod

from vsc.utils import fancylogger


class SubCommand(object):
    """Abstract base class for subcommand support."""

    CMD = None
    EXAMPLE = None
    HELP = None

    def __init__(self, *args, **kwargs):
        """Class constructor."""
        self.envvar_prefix = 'HOD_%s' % self.CMD.upper().replace('-', '_')
        self.usage_txt = 'hod %s [options]' % self.CMD
        self.log = fancylogger.getLogger(name=self.__class__.__name__, fname=False)

    def usage(self):
        """Return usage of this subcommand."""
        usage = "hod %s - %s\n" % (self.CMD, self.HELP)
        if self.EXAMPLE:
            usage += "hod %s %s\n" % (self.CMD, self.EXAMPLE)
        return usage

    def _log_and_raise(self, err):
        """Report error that occured, and raise Exception"""
        fancylogger.setLogFormat(fancylogger.TEST_LOGGING_FORMAT)
        fancylogger.logToScreen(enable=True)
        self.log.raiseException(str(err))

    def report_error(self, msg, *args):
        """Report error and exit"""
        self.log.error(msg, *args)
        sys.exit(1)

    @abstractmethod
    def run(self, args):
        '''Run the command'''
        pass
