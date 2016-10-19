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
Hanythingondemand main program.

@author: Ewan Higgs (Universiteit Gent)
@author: Kenneth Hoste (Universiteit Gent)
"""
from vsc.utils import fancylogger

COMMON_HOD_CONFIG_OPTIONS = {
    'modulepaths': ("Extra paths to take into account for loading modules", 'string', 'store', None),
    'modules': ("Extra modules to load in each service environment", 'string', 'store', None),
}

GENERAL_HOD_OPTIONS = {
    'dist': ("Prepackaged Hadoop distribution (e.g.  Hadoop/2.5.0-cdh5.3.1-native). "
             "This cannot be set if --hodconf is set", 'string', 'store', None),
    'hodconf': ("Top level configuration file. This can be a comma separated list of config files with "
                "the later files taking precendence.", 'string', 'store', None),
    'hod-module': ("Module to load for hanythingondemand in submitted job", 'string', 'store', None),
    'label': ("Cluster label", 'string', 'store', None),
    'workdir': ("Working directory", 'string', 'store', None),
}

RESOURCE_MANAGER_OPTIONS = {
    'walltime': ("Job walltime in hours", 'float', 'store', 48, 'l'),
    'nodes': ("Full nodes for the job", "int", "store", 1, "n"),
    'ppn': ("Processors per node (-1=full node)", "int", "store", -1),
    'mail': ("When to send mail (b=begin, e=end, a=abort)", "string", "extend", [], "m"),
    'mailothers': ("Other email adresses to send mail to", "string", "extend", [], "M"),
    'queue': ("Queue name (empty string is default queue)", "string", "store", "", "q"),
    'partition': ("Partition name (empty string is default partition)", "string", "store", "", "p"),
    'account': ("Account name (empty string is default Account)", "string", "store", "", "A"),
}

_log = fancylogger.getLogger('create', fname=False)

def validate_required_option(options):
    """pbs options require a config and a workdir"""
    if not options.hodconf and not options.dist:
        _log.error('Either --hodconf or --dist must be set')
        return False
    if options.hodconf and options.dist:
        _log.error('Only one of --hodconf or --dist can be set')
        return False
    if not options.workdir:
        _log.error('No workdir ("--workdir") provided')
        return False

    return True

def validate_pbs_option(options):
    """pbs options require a config and a workdir"""
    if not validate_required_option(options):
        return False
    if not options.hod_module:
        _log.error('No hod-module ("--hod-module") provided')
        return False

    return True
