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
import os
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
        opts.update({
            'modules': ("Extra modules to load in each service environment", 'string', 'store', None),
        })
        descr = ["Local configuration", "Configuration options for the 'genconfig' subcommand"]

        self.log.debug("Add config option parser descr %s opts %s", descr, opts)
        self.add_group_parser(opts, descr)


def cluster_config_dir():
    """
    Determine cluster configuration directory.
    Returns $XDG_CONFIG_HOME/hod.d or $HOME/.config/hod.d
    http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """
    dflt = os.path.join(os.getenv('HOME'), '.config')
    return os.path.join(os.getenv('XDG_CONFIG_HOME', dflt), 'hod.d')


def known_cluster_labels():
    """
    Return list of known cluster labels.
    """
    path = cluster_config_dir()
    if os.path.exists(path):
        os.listdir(path)
    else:
        _log.warning("No cluster config directory '%s' (yet)", path)
        return []


def cluster_env_file(label):
    """
    Return path to env file for cluster with specified label.
    """
    if label in known_cluster_labels():
        env_script = os.path.join(cluster_config_dir, label, 'env')
        if os.path.exists(env_script):
            return env_script
        else:
            _log.error("No 'env' file found for cluster with label '%s'", label)
            sys.exit(1)
    else:
        _log.error("Unknown cluster label '%s': %s", label, known_cluster_labels())
        sys.exit(1)


def create_env_file():
    """Create env file that can be source when connecting to the current hanythingondemand cluster."""
    raise NotImplementedError


def main(args):
    """Run HOD cluster."""
    options = LocalOptions(go_args=args)

    if MPI.COMM_WORLD.rank == MASTERRANK:
        _log.debug("Creating env file")
        create_env_file()
        _log.debug("Starting master process")
        svc = ConfiguredMaster(options)
    else:
        _log.debug("Starting slave process")
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
