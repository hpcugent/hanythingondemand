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
import sys

from hod.subcommands import create, listcmd, genconfig, helptemplate, dists


SUBCOMMANDS = [
    create.CreateSubCommand,
    listcmd.ListSubCommand,
    dists.DistsSubCommand,
    helptemplate.HelpTemplateSubCommand,
    genconfig.GenConfigSubCommand,
]

SUBCOMMAND_CLASSES = dict([(sc.CMD, sc) for sc in SUBCOMMANDS])


def usage():
    """Print the usage information for 'hod'."""
    usage = "hod: hanythingondemand - Run services within an HPC cluster\n"
    usage += "usage: hod [--version] [--help] <subcommand> [subcommand options]\n"
    usage += "Available subcommands:\n"
    for sc in SUBCOMMANDS:
        usage += '    {0:16}{1}\n'.format(sc.CMD, sc.HELP)

    return usage


def main(args):
    """Parse options and run specified subcommand."""
    # check if a subcommand is specified
    subcmd_class = None
    for subcmd in SUBCOMMAND_CLASSES:
        if subcmd in args:
            subcmd_class = SUBCOMMAND_CLASSES[subcmd]
            break

    if subcmd_class:
        subcmd_class().run(args[1:].remove(subcmd))

    elif len([arg for arg in args if not arg.startswith('-')]) > 1:
        sys.stderr.write("ERROR: No known subcommand specified")
        sys.stderr.write(usage())
        sys.exit(1)
    else:
        # no subcommand provided, print usage info
        print usage()
        sys.exit(0)

if __name__ == '__main__':
    main(sys.argv)
