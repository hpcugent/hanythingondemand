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
Cluster and label functions.

@author: Ewan Higgs (Universiteit Gent)
@author: Kenneth Hoste (Universiteit Gent)
"""

import os
import sys
import shutil
from collections import namedtuple

from vsc.utils import fancylogger

from hod.config.config import resolve_config_paths
import hod.config.config as hc


_log = fancylogger.getLogger(fname=False)


CLUSTER_ENV_TEMPLATE = """
# make sure session is properly set up (e.g., that 'module' command is defined)
source /etc/profile

for modpath in %(modpaths)s; do module use $modpath; done

module load %(modules)s

# set up environment
export HADOOP_CONF_DIR='%(hadoop_conf_dir)s'
export HBASE_CONF_DIR='%(hadoop_conf_dir)s'
export HOD_LOCALWORKDIR='%(hod_localworkdir)s'
# TODO: HADOOP_LOG_DIR?

echo "Welcome to your hanythingondemand cluster (label: %(label)s)"
echo
echo "Relevant environment variables:"
env | egrep '^HADOOP_|^HOD_|PBS_JOBID|MODULEPATH' | sort
echo
echo "List of loaded modules:"
module list 2>&1
"""


ClusterInfo = namedtuple('ClusterInfo', 'label, jobid, pbsjob')

def is_valid_label(label):
    """
    Checks if a label provided on the command line is a valid filename by making
    sure it doesn't have directory splitting characters in it.

    Because user provided labels are optional, None is also a valid label. It
    just means we will use the job id for the label.
    """
    return label is None or os.path.basename(label) == label


def validate_label(label, known_labels):
    """
    Return true if a label is valid; false otherwise.  If it is invalid, report why to stderr.
    This is a convenience function used in 'hod batch' and 'hod create'
    """
    if not is_valid_label(label):
        sys.stderr.write("Tried to submit HOD cluster with label '%s' but it is not a valid label\n" % label)
        sys.stderr.write("Labels are used as filenames so they cannot have %s characters\n" % os.sep)
        return False

    if label in known_labels:
        sys.stderr.write("Tried to submit HOD cluster with label '%s' but it already exists\n" % label)
        sys.stderr.write("If it is an old HOD cluster, you can remove it with `hod clean`\n")
        return False

    return True

def validate_hodconf_or_dist(hodconf, dist):
    """
    Returns true if either the hodconf or the dist can be resolved successfully.
    If it cannot be resolved, an error is logged and false is returned..
    """
    try:
        resolve_config_paths(hodconf, dist)
    except ValueError as e:
        _log.error(e)
        return False
    return True

def report_cluster_submission(label):
    """
    Report to stdout that a cluster has been submitted.
    This is a convenience function used in 'hod batch' and 'hod create'
    """
    if label is None:
        print "Submitting HOD cluster with no label (job id will be used as a default label) ..."
    else:
        print "Submitting HOD cluster with label '%s'..." % label


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
        info_filepath = os.path.join(cluster_info_dir(), label, info_file)
        if os.path.exists(info_filepath):
            return info_filepath
        else:
            raise ValueError("No '%s' file found for cluster with label '%s'" % (info_file, label))
    else:
        raise ValueError("Unknown cluster label '%s': %s" % (label, labels))


def cluster_jobid(label):
    """Return job ID for cluster with specified label."""
    return open(_cluster_info(label, 'jobid')).read()


def cluster_workdir(label):
    """Return workdir for cluster with specified label."""
    return os.path.expandvars(open(_cluster_info(label, 'workdir')).read())


def _find_pbsjob(jobid, pbsjobs):
    for job in pbsjobs:
        if jobid == job.jobid:
            return job
    return None


def mk_cluster_info_dict(labels, pbsjobs, master=None):
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
        except ValueError as e:
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
    hodconf = hc.load_hod_config(config_path, options.workdir, options.modulepaths, options.modules)
    cluster_info = {
        'hadoop_conf_dir': hodconf.configdir,
        'hod_localworkdir': hodconf.localworkdir,
        'label': label,
        'modpaths': ' '.join(hodconf.modulepaths),
        'modules': ' '.join(hodconf.modules),
        'workdir': options.workdir
    }
    return cluster_info


def mk_cluster_info(label, jobid, workdir):
    """
    Given a label and PbsJob, create the hod.d/<label> directory.
    This is created after the job is submitted, but before the job is run.
    """
    if label is None:
        label = jobid
    info_dir = os.path.join(cluster_info_dir(), label)
    try:
        if not os.path.exists(info_dir):
            os.makedirs(info_dir)
    except OSError as err:
        _log.error("Failed to create cluster info dir '%s': %s", info_dir, err)
        raise

    try:
        with open(os.path.join(info_dir, 'jobid'), 'w') as jobid_file:
            jobid_file.write(jobid)
    except IOError as err:
        _log.error("Failed to write jobid file: %s", err)
        raise

    try:
        with open(os.path.join(info_dir, 'workdir'), 'w') as workdir_file:
            workdir_file.write(workdir)
    except IOError as err:
        _log.error("Failed to write workdir file: %s", err)
        raise


def save_cluster_info(cluster_info):
    """
    Save info (job ID, env script, ...) for this cluster in the cluster info dir.
    cluster_info is a dict created by `gen_cluster_info` (not a ClusterInfo instance)
    """
    info_dir = os.path.join(cluster_info_dir(), cluster_info['label'])
    jobid = os.getenv('PBS_JOBID', 'PBS_JOBID_NOT_DEFINED')

    if not cluster_info_exists(cluster_info['label']):
        _log.warn("Cluster info directory not found. Creating it now""")
        mk_cluster_info(cluster_info['label'], jobid, cluster_info['workdir'])

    env_script_txt = generate_cluster_env_script(cluster_info)

    with open(os.path.join(info_dir, 'env'), 'w') as env_script:
        env_script.write(env_script_txt)


def clean_cluster_info(master, cluster_info):
    """
    Remove all the cluster directories for the labels with jobids using the
    master, but no job info founs.
    """
    for info in cluster_info:
        if info.pbsjob is None and info.jobid.endswith(master):
            rm_cluster_localworkdir(info.label)
            rm_cluster_info(info.label)


def cluster_info_exists(label):
    """Returns whether a cluster info directory with jobid file exists."""
    info_dir = os.path.join(cluster_info_dir(), label)
    return os.path.exists(info_dir) and os.path.exists(os.path.join(info_dir, 'jobid'))


def rm_cluster_info(label):
    """Remove a cluster label directory"""
    info_dir = os.path.join(cluster_info_dir(), label)
    shutil.rmtree(info_dir)
    print 'Removed cluster info directory %s for cluster labeled %s' % (info_dir, label)


def rm_cluster_localworkdir(label):
    """Remove a cluster localworkdir directory"""
    jobid = cluster_jobid(label)
    workdir = cluster_workdir(label)
    jobid_workdir = os.path.join(workdir, 'hod', jobid)
    if os.path.exists(jobid_workdir):
        shutil.rmtree(jobid_workdir)
        print 'Removed cluster localworkdir directory %s for cluster labeled %s' % (jobid_workdir, label)
    else:
        print 'Note: No local workdir %s found for cluster %s; job was deleted before it started running?' % (jobid_workdir, label)


def mv_cluster_info(label, newlabel):
    """Remove a cluster label directory"""
    cid = cluster_info_dir()
    labeldir = os.path.join(cid, label)
    newlabeldir = os.path.join(cid, newlabel)
    shutil.move(labeldir, newlabeldir)


def post_job_submission(label, jobs, workdir):
    """
    Report the jobs and write hod.d/ files that have been submitted by create
    and batch.
    """
    if not jobs:
        sys.stderr.write('Error: No jobs found after submission.\n')
        sys.exit(1)
    elif len(jobs) > 1:
        sys.stderr.write('Warning: More than one job found: %s\n' % str([j.jobid for j in jobs]))
    job = jobs[0]
    print "Job submitted: %s" % str(job)
    try:
        mk_cluster_info(label, job.jobid, workdir)
    except (IOError, OSError) as e:
        sys.stderr.write('Failed to write out cluster files. You will not be able to use `hod connect "%s"`: %s.\n' % (label, e))
        sys.exit(1)
