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
"""
Print out template parameters used by hod.

@author: Ewan Higgs (Ghent University)
@author: Kenneth Hoste (Ghent University)
"""
import os
from vsc.utils.generaloption import GeneralOption

import hod.config.template as hct
import hod.table as ht
from hod import VERSION as HOD_VERSION
from hod.subcommands.subcommand import SubCommand
from hod.mpiservice import master_template_opts
from hod.config.config import ConfigOptsParams
from hod.commands.command import COMMAND_TIMEOUT
from hod.utils import setup_diagnostic_environment


class HelpTemplateOptions(GeneralOption):
    """Option parser for 'list' subcommand."""
    VERSION = HOD_VERSION


def mk_registry():
    """Make a TemplateRegistry and register basic items"""
    config_opts = ConfigOptsParams('svc-name', 'MASTER', 'ExecPreStart', 'ExecStart', 'ExecStop',
                                   dict(), workdir='WORKDIR', modulepaths=['MODULEPATHS'],
                                   modules=['MODULES'], master_template_kwargs=[], timeout=COMMAND_TIMEOUT)
    reg = hct.TemplateRegistry()
    hct.register_templates(reg, config_opts)
    master_template_kwargs = master_template_opts(reg.fields.values())
    for ct in master_template_kwargs:
        reg.register(ct)
    return reg


def format_rows(fields, resolver):
    """
    Given a list of fields, return the template substituted versions of the text
    """
    rows = []
    for val in sorted(fields.values(), key=lambda x: x.name):
        rows.append((val.name, resolver('$%s' % val.name), val.doc))
    return rows

class HelpTemplateSubCommand(SubCommand):
    """Implementation of 'help-template' subcommand."""
    CMD = 'help-template'
    EXAMPLE = None
    HELP = "Print the values of the configuration templates based on the current machine."

    def run(self, args):
        """Run 'help-template' subcommand."""
        setup_diagnostic_environment()

        _ = HelpTemplateOptions(go_args=args, envvar_prefix=self.envvar_prefix, usage=self.usage_txt)
        reg = mk_registry()
        resolver = hct.TemplateResolver(**reg.to_kwargs())
        print 'Hanythingondemand template parameters'
        headers = ('Parameter name', 'Value', 'Documentation')
        formatted_rows = format_rows(reg.fields, resolver)
        print ht.format_table(formatted_rows, headers)
