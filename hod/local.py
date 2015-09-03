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
import random
import string
import sys

from hod import VERSION as HOD_VERSION

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

from hod.config.config import resolve_config_paths
from hod.hodproc import ConfiguredSlave, ConfiguredMaster, load_hod_config
from hod.mpiservice import MASTERRANK, run_tasks, setup_tasks
from hod.options import GENERAL_HOD_OPTIONS

try:
    from mpi4py import MPI
    # mpi4py is available, no need guard against import errors
    def mpi4py_is_available(fn):
        """No-op decorator."""
        return fn

except ImportError as err:
    def mpi4py_is_available(_):
        """Decorator which raises an ImportError because mpi4py is not available."""
        def fail(*args, **kwargs):
            """Raise ImportError since mpi4py is not available."""
            raise ImportError("%s; is there an environment module providing MPI support loaded?" % err)

        return fail


CLUSTER_ENV_TEMPLATE = """
# make sure session is properly set up (e.g., that 'module' command is defined)
source /etc/profile

# set up environment
export HADOOP_CONF_DIR='%(hadoop_conf_dir)s'
export HOD_LOCALWORKDIR='%(hod_localworkdir)s'
# TODO: HADOOP_LOG_DIR?
module load %(modules)s

echo "Welcome to your hanythingondemand cluster (label: %(label)s)"
echo
echo "Relevant environment variables:"
env | egrep '^HADOOP_|^HOD_|PBS_JOBID' | sort
echo
echo "List of loaded modules:"
module list 2>&1
"""


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


def cluster_info_dir():
    """
    Determine cluster info directory.
    Returns $XDG_CONFIG_HOME/hod.d or $HOME/.config/hod.d
    http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """
    dflt = os.path.join(os.getenv('HOME', ''), '.config')
    return os.path.join(os.getenv('XDG_CONFIG_HOME', dflt), 'hod.d')


def known_cluster_labels():
    """
    Return list of known cluster labels.
    """
    path = cluster_info_dir()
    if os.path.exists(path):
        return os.listdir(path)
    else:
        _log.warning("No cluster config directory '%s' (yet)", path)
        return []


def _cluster_info(label, info_file):
    """
    Return path to specified cluster info file for cluster with specified label.
    @param label: cluster label
    @param info_file: type of info to return (env, jobid, ...)
    """
    labels = known_cluster_labels()
    if label in labels:
        info_file = os.path.join(cluster_info_dir(), label, info_file)
        if os.path.exists(info_file):
            return info_file
        else:
            raise ValueError("No 'env' file found for cluster with label '%s'" % label)
    else:
        raise ValueError("Unknown cluster label '%s': %s" % (label, labels))


def cluster_jobid(label):
    """Return job ID for cluster with specified label."""
    return open(_cluster_info(label, 'jobid')).read()


def cluster_env_file(label):
    """
    Return path to env file for cluster with specified label.
    """
    return _cluster_info(label, 'env')


def generate_cluster_env_script(cluster_info):
    """
    Generate the env script for this cluster.
    """
    return CLUSTER_ENV_TEMPLATE % cluster_info


def gen_cluster_info(label, options):
    """Generate cluster info as a dict, intended to use as template values for CLUSTER_ENV_TEMPLATE."""
    # list of modules that should be loaded: modules for selected service + extra modules specified via --modules
    config_path = resolve_config_paths(options.hodconf, options.dist)
    hodconf = load_hod_config(config_path, options.workdir, options.modules)
    cluster_info = {
        'hadoop_conf_dir': hodconf.configdir,
        'hod_localworkdir': hodconf.localworkdir,
        'label': label,
        'modules': ' '.join(hodconf.modules),
    }
    return cluster_info


def save_cluster_info(cluster_info):
    """Save info (job ID, env script, ...) for this cluster in the cluster info dir."""
    info_dir = os.path.join(cluster_info_dir(), cluster_info['label'])
    try:
        if not os.path.exists(info_dir):
            os.makedirs(info_dir)
    except OSError as err:
        _log.error("Failed to create cluster info dir '%s': %s", info_dir, err)

    try:
        with open(os.path.join(info_dir, 'jobid'), 'w') as jobid:
            jobid.write(os.getenv('PBS_JOBID', 'PBS_JOBID_NOT_DEFINED'))

        env_script_txt = generate_cluster_env_script(cluster_info)

        with open(os.path.join(info_dir, 'env'), 'w') as env_script:
            env_script.write(env_script_txt)
    except IOError as err:
        _log.error("Failed to write cluster info files: %s", err)


@mpi4py_is_available
def main(args):
    """Run HOD cluster."""
    optparser = LocalOptions(go_args=args)

    if MPI.COMM_WORLD.rank == MASTERRANK:
        label = optparser.options.label
        if label is None:
            # if no label is specified, use job ID;
            # if $PBS_JOBID is not set, generate a random string (10 chars)
            label = os.getenv('PBS_JOBID', ''.join(random.choice(string.letters + string.digits) for _ in range(10)))

        _log.debug("Creating cluster info using label '%s'", label)
        cluster_info = gen_cluster_info(label, optparser.options)
        save_cluster_info(cluster_info)

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
