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
"""
Print out template parameters used by hod.

@author: Ewan Higgs (Ghent University)
@author: Kenneth Hoste (Ghent University)
"""
from vsc.utils.generaloption import GeneralOption

import hod.config.template as hct
from hod import VERSION as HOD_VERSION
from hod.subcommands.subcommand import SubCommand
from hod.mpiservice import master_template_opts
from hod.config.config import ConfigOptsParams


class HelpTemplateOptions(GeneralOption):
    """Option parser for 'list' subcommand."""
    VERSION = HOD_VERSION


def mk_registry():
    """Make a TemplateRegistry and register basic items"""
    config_opts = ConfigOptsParams('svc-name', 'MASTER', 'ExecPreStart',
            'ExecStart', 'ExecStop', dict(), workdir='WORKDIR',
        modules=['MODULES'], master_template_kwargs=[])
    reg = hct.TemplateRegistry()
    hct.register_templates(reg, config_opts)
    master_template_kwargs = master_template_opts(reg.fields.values())
    for ct in master_template_kwargs:
        reg.register(ct)
    return reg


def mk_fmt_str(fields, resolver):
    """Calculate the format string for printing the template parameters."""
    longest_name = max(fields.values(), key=lambda x: len(x.name)).name
    max_name_len = len(longest_name)
    value_names = map(resolver, ['$%s'% v.name for v in fields.values()])
    longest_value = max(value_names, key=len)
    max_val_len = len(longest_value)
    return '%%-%ds:\t%%-%ds\t%%s' % (max_name_len, max_val_len)


class HelpTemplateSubCommand(SubCommand):
    """Implementation of 'help-template' subcommand."""
    CMD = 'help-template'
    EXAMPLE = None
    HELP = "Print the values of the configuration templates based on the current machine."

    def run(self, args):
        """Run 'help-template' subcommand."""
        optparser = HelpTemplateOptions(go_args=args, envvar_prefix=self.envvar_prefix, usage=self.usage_txt)
        reg = mk_registry()
        resolver = hct.TemplateResolver(**reg.to_kwargs())
        print 'Hanythingondemand template parameters'
        fmt_str = mk_fmt_str(reg.fields, resolver)
        print fmt_str % ('Parameter name', 'Value', 'Documentation')
        for v in sorted(reg.fields.values(), key=lambda x: x.name):
            print fmt_str % (v.name, resolver('$%s' % v.name), v.doc)
