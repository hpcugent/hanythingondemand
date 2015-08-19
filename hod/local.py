#!/usr/bin/env python
# ##
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
Main hanythingondemand script, should be invoked in a job

@author: Ewan Higgs (Universiteit Gent)
@author: Kenneth Hoste (Universiteit Gent)
"""
import copy
import sys
from mpi4py import MPI

from hod import VERSION as HOD_VERSION

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

from hod.hodproc import ConfiguredSlave, ConfiguredMaster
from hod.mpiservice import MASTERRANK, run_tasks, setup_tasks
from hod.options import GENERAL_HOD_OPTIONS


_log = fancylogger.getLogger(fname=False)


class LocalOptions(GeneralOption):
    """Option parser for 'genconfig' subcommand."""
    VERSION = HOD_VERSION

    def config_options(self):
        """Add general configuration options."""
        opts = copy.deepcopy(GENERAL_HOD_OPTIONS)
        descr = ["Local configuration", "Configuration options for the 'genconfig' subcommand"]

        self.log.debug("Add config option parser descr %s opts %s", descr, opts)
        self.add_group_parser(opts, descr)


def main(args):
    """Run HOD cluster."""
    options = LocalOptions(go_args=args)

    if MPI.COMM_WORLD.rank == MASTERRANK:
        _log.debug('Starting master process')
        svc = ConfiguredMaster(options)
    else:
        _log.debug('Starting slave process')
        svc = ConfiguredSlave(options)
    try:
        setup_tasks(svc)
        run_tasks(svc)
        svc.stop_service()
    except Exception as err:
        _log.error(str(err))
        _log.exception("HanythingOnDemand failed")
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
