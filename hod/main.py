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
import sys

import hod
from hod.subcommands import (batch, connect, clean, clone, create, destroy, dists, genconfig,
        helptemplate, listcmd, relabel)


SUBCOMMANDS = [
    batch.BatchSubCommand,
    clean.CleanSubCommand,
    clone.CloneSubCommand,
    connect.ConnectSubCommand,
    create.CreateSubCommand,
    destroy.DestroySubCommand,
    dists.DistsSubCommand,
    genconfig.GenConfigSubCommand,
    helptemplate.HelpTemplateSubCommand,
    listcmd.ListSubCommand,
    relabel.RelabelSubCommand,
]

SUBCOMMAND_CLASSES = dict([(sc.CMD, sc) for sc in SUBCOMMANDS])


def usage():
    """Print the usage information for 'hod'."""
    usage = "%s version %s - Run services within an HPC cluster\n" % (hod.NAME, hod.VERSION)
    usage += "usage: hod <subcommand> [subcommand options]\n"
    usage += "Available subcommands (one of these must be specified!):\n"
    for sc in SUBCOMMANDS:
        usage += '    {0:16}{1}\n'.format(sc.CMD, sc.HELP)

    return usage


def init_subcmd(args):
    """Initialize subcommand based on specified arguments; returns None is no subcommand was found."""
    for subcmd in SUBCOMMAND_CLASSES:
        if subcmd in args:
            subcmd_class = SUBCOMMAND_CLASSES[subcmd]
            return subcmd_class(), args[1:].remove(subcmd)
    return None, args


def main(args):
    """Parse options and run specified subcommand."""
    subcmd, args = init_subcmd(args)
    if subcmd is not None:
        return subcmd.run(args)

    elif len([arg for arg in args if not arg.startswith('-')]) > 1:
        sys.stderr.write("ERROR: No known subcommand specified\n")
        sys.stderr.write(usage())
        return 1
    else:
        # no subcommand provided, print usage info
        print usage()
        return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
