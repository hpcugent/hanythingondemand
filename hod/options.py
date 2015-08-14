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
Hanythingondemand main program.

@author: Ewan Higgs (Universiteit Gent)
@author: Kenneth Hoste (Universiteit Gent)
"""
from vsc.utils import fancylogger

GENERAL_HOD_OPTIONS = {
    'hodconf': ("Top level configuration file. This can be a comma separated list of config files with "
                "the later files taking precendence.", 'string', 'store', None),
    'dist': ("Prepackaged Hadoop distribution (e.g.  Hadoop/2.5.0-cdh5.3.1-native). "
             "This cannot be set if --hodconf is set", 'string', 'store', None),
    'workdir': ("Working directory", 'string', 'store', None),
}


_log = fancylogger.getLogger('create', fname=False)


def validate_pbs_option(options):
    """pbs options require a config and a workdir"""
    if not options.options.hodconf and not options.options.dist:
        _log.error('Either --hodconf or --dist must be set')
        return False
    if options.options.hodconf and options.options.dist:
        _log.error('Only one of --hodconf or --dist can be set')
        return False
    if not options.options.workdir:
        _log.error('No workdir ("--workdir") provided')
        return False
    return True
