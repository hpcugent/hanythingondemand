#!/usr/bin/env python
# ##
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
Main hanythingondemand script, should be invoked in a job

@author: Ewan Higgs (Universiteit Gent)
@author: Kenneth Hoste (Universiteit Gent)
"""
import copy
import os
import random
import string
import sys

from hod import VERSION as HOD_VERSION

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

from hod.config.config import resolve_config_paths
from hod.cluster import gen_cluster_info, save_cluster_info
from hod.hodproc import ConfiguredSlave, ConfiguredMaster
from hod.mpiservice import MASTERRANK, run_tasks, setup_tasks
from hod.options import COMMON_HOD_CONFIG_OPTIONS, GENERAL_HOD_OPTIONS
from hod.utils import only_if_module_is_available

# optional packages, not always required
try:
    from mpi4py import MPI
except ImportError:
    pass


_log = fancylogger.getLogger(fname=False)


class LocalOptions(GeneralOption):
    """Option parser for 'genconfig' subcommand."""
    VERSION = HOD_VERSION

    def config_options(self):
        """Add general configuration options."""
        opts = copy.deepcopy(GENERAL_HOD_OPTIONS)
        opts.update(COMMON_HOD_CONFIG_OPTIONS)
        opts.update({
            'script': ("Script to run on the cluster", "string", "store", None),
        })
        descr = ["Local configuration", "Configuration options for the 'genconfig' subcommand"]

        self.log.debug("Add config option parser descr %s opts %s", descr, opts)
        self.add_group_parser(opts, descr)


@only_if_module_is_available('mpi4py')
def main(args):
    """Run HOD cluster."""
    optparser = LocalOptions(go_args=args)

    if MPI.COMM_WORLD.rank == MASTERRANK:
        label = optparser.options.label
        if label is None:
            # if no label is specified, use job ID;
            # if $PBS_JOBID is not set, generate a random string (10 chars)
            label = os.getenv('PBS_JOBID', ''.join(random.choice(string.letters + string.digits) for _ in range(10)))
            optparser.options.label = label

        _log.debug("Creating cluster info using label '%s'", label)
        cluster_info = gen_cluster_info(label, optparser.options)
        try:
            save_cluster_info(cluster_info)
        except (IOError, OSError) as e:
            _log.error("Failed to save cluster info files: %s", e)
            sys.exit(1)

        _log.debug("Starting master process")
        svc = ConfiguredMaster(optparser.options)
    else:
        _log.debug("Starting slave process")
        svc = ConfiguredSlave(optparser.options)

    try:
        setup_tasks(svc)
        run_tasks(svc)
        svc.stop_service()
        return 0
    except Exception as err:
        _log.error(str(err))
        _log.exception("HanythingOnDemand failed")
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
