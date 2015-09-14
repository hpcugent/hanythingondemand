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
Cluster and label functions.

@author: Ewan Higgs (Universiteit Gent)
@author: Kenneth Hoste (Universiteit Gent)
"""

import os
import shutil
from collections import namedtuple

from vsc.utils import fancylogger

from hod.config.config import resolve_config_paths
from hod.hodproc import load_hod_config


_log = fancylogger.getLogger(fname=False)


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


ClusterInfo = namedtuple('ClusterInfo', 'label, jobid, pbsjob')


def cluster_info_dir():
    """
    Determine cluster info directory.
    Returns $XDG_CONFIG_HOME/hod.d or $HOME/.config/hod.d
    http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """
    dflt = os.path.join(os.path.expanduser('~'), '.config')
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


def _find_pbsjob(jobid, pbsjobs):
    for job in pbsjobs:
        if jobid == job.jobid:
            return job
    return None


def mk_cluster_info(labels, pbsjobs, master=None):
    """
    Given a list of labels and PbsJobs, construct a dict of list of tuples
    mapping label to PbsJob.
    """
    info = []
    seen_jobs = set()

    # All the clusters with labels
    for label in labels:
        try:
            jobid = cluster_jobid(label)
            if master is not None and not jobid.endswith(master):
                continue
            job = _find_pbsjob(jobid, pbsjobs)
            if job is not None:
                seen_jobs.add(jobid)
        except ValueError, e:
            job = None
        info.append(ClusterInfo(label, jobid, job))

    return info


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


def clean_cluster_info(master, cluster_info):
    """
    Remove all the cluster directories for the labels with jobids using the
    master, but no job info founs.
    """
    for info in cluster_info:
        if info.pbsjob is None and info.jobid.endswith(master):
            rm_cluster_info(info.label)

def rm_cluster_info(label):
    """Remove a cluster label directory"""
    info_dir = os.path.join(cluster_info_dir(), label)
    shutil.rmtree(info_dir)
    print 'Removed cluster info directory %s for cluster labeled %s' % (info_dir, label)
