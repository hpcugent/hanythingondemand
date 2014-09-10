# #
# Copyright 2009-2013 Ghent University
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

@author: Stijn De Weirdt
"""
import time
import os
from mpi4py import MPI

from hod.node import Node
import hod.node as node
from vsc import fancylogger
from collections import namedtuple
import socket

from vsc.utils import fancylogger
_log = fancylogger.getLogger(fname=False)

__all__ = ['MASTERRANK', 'Task', 'barrier', 'MpiService', 'setup_tasks',
        'run_tasks']

MASTERRANK = 0

Task = namedtuple('Task', ['type', 'ranks', 'options', 'master_env'])

def _who_is_out_there(comm, rank):
    """Get all self.ranks of members of communicator"""
    others = comm.allgather(rank)
    _log.debug("Are out there %s on comm %s" % (others, comm))
    return others

def _check_comm(comm, txt):
    """Report details about communicator"""
    if comm == MPI.COMM_NULL:
        _log.debug("%scomm %s" % (txt, comm))
    else:
        myrank = comm.Get_rank()
        mysize = comm.Get_size()
        if comm == MPI.COMM_WORLD:
            _log.debug("%s comm WORLD %s size %d rank %d" %
                           (txt, comm, mysize, myrank))
        else:
            _log.debug(
                "%scomm %s size %d rank %d" % (txt, comm, mysize, myrank))

def barrier(comm, txt):
    """Perform MPI.barrier"""
    _log.debug("%s with barrier" % txt)
    comm.barrier()
    _log.debug("%s with barrier DONE" % txt)

def _make_topology_comm(comm, allnodes, size, rank):
    """Given the Node topology info, make communicator per dimension"""
    topocom = [] # comm not part of topocom by default

    topo = allnodes[rank]['topology']
    dimension = len(topo)  # all nodes have same dimension (see sanity check)
    mykeys = [[]] * dimension

    # # sanity check
    # # - all topologies have same length
    foundproblem = False
    for n in range(size):
        sometopo = allnodes[n]['topology']
        if dimension == len(sometopo):
            for dim in range(dimension):
                if topo[dim] == sometopo[dim]:
                    # add the rank of somenode to the mykeys list in proper dimension
                    mykeys[dim].append(n)
        else:
            _log.error("Topology size of this Node %d does not match that of rank %d (size %d)" % (dimension, n, len(sometopo)))
            foundproblem = True

    if foundproblem:
        _log.error("Found an irregularity. Not creating the topology communicators")
        return

    _log.debug("List to determine keys %s" % mykeys)
    _log.debug("Creating communicators per dimension (total dimension %d)" % dimension)
    for dimind in range(dimension):
        color = topo[dimind]  # identify newcomm
        key = mykeys[dimind].index(rank)  # rank in newcomm
        newcomm = comm.Split(
            color, key)  # non-overlapping communicator
        _check_comm(newcomm, "Topologycomm dimensionindex %d color %d key %d" % (dimind, color, key))
        # # sanity check
        others = _who_is_out_there(newcomm, rank)
        _log.debug(
            "Others found %s; based on %s" % (others, mykeys[dimind]))
        if mykeys[dimind] == others:
            _log.debug("Others %s in comm matches based input %s. Adding to topocom." % (others, mykeys[dimind]))
            topocom.append(newcomm)
        else:
            _log.error("Others %s in comm don't match based input %s. Adding COMM_NULL to topocom." % (others, mykeys[dimind]))  # TODO is adding COMM_NULL a good idea?
            topocom.append(MPI.COMM_NULL)
    return topocom

def _collect_nodes(comm, size):
    """Collect local Node info and distribute it over all nodes"""
    node = Node()
    descr = node.go()
    _log.debug("Got Node %s" % node)

    allnodes = comm.alltoall([descr] * size)

    # # TODO proper sanity check to see if all nodes have similar network
    # (ie that the netmask of the selected index can reach the other indices)
    _log.debug("Sanity check: do all nodes have same network adapters?")
    is_ok = True
    for intf in descr['network']:
        dev = intf[2]
        alldevs = [[y[2] for y in x['network']] for x in allnodes]
        for rnk in range(size):
            if not dev in alldevs[rnk]:
                _log.error("no dev %s found in alldevs %s of rank %s" %
                               (dev, alldevs[rnk], rnk))
                is_ok = False

    if is_ok:
        _log.debug("Sanity check ok")
    else:
        _log.error("Sanity check failed")

    return allnodes

def _check_group(group, txt):
    """Report details about group"""
    myrank = group.Get_rank()
    mysize = group.Get_size()
    _log.debug(
        "%s group %s size %d rank %d" % (txt, group, mysize, myrank))

def _make_comm_group(comm, ranks):
    """Make a new communicator based on set of ranks"""
    mygroup = comm.Get_group()
    _log.debug("Creating newgroup using ranks %s from group %s" %
                   (ranks, mygroup))
    newgroup = mygroup.Incl(ranks)
    _check_group(newgroup, 'make_comm_group')

    newcomm = comm.Create(newgroup)
    _check_comm(newcomm, 'make_comm_group')

    return newcomm

def _stop_comm(comm):
    """Stop a single communicator"""
    _check_comm(comm, 'Stopping')

    if comm == MPI.COMM_NULL:
        _log.debug("No disconnect COMM_NULL")
        return

    barrier(comm, 'Stop')

    if comm == MPI.COMM_WORLD:
        _log.debug("No disconnect COMM_WORLD")
    else:
        _log.debug("Stop disconnect")
        comm.Disconnect()


def _master_spread(comm, tasks):
    retval = comm.bcast(tasks, root=MASTERRANK)
    _log.debug("Distributed '%s' from masterrank %s" % (tasks, MASTERRANK))
    return retval

def _slave_spread(comm):
    tasks = comm.bcast(root=MASTERRANK)
    _log.debug("Received '%s' from masterrank %s" % (tasks, MASTERRANK))
    return tasks


def setup_tasks(svc):
    """Setup the per node services and spread the tasks out."""
    _log.debug("No tasks found. Running distribution and spread.")


    # Configure
    if svc.rank == MASTERRANK:
        master_data_hostname = node.sorted_network(node.get_networks())[0].hostname
        master_template_kwargs = dict(masterhostname=socket.getfqdn(),
            masterdatahostname=master_data_hostname)
        _master_spread(svc.comm, master_template_kwargs)
    else:
        master_template_kwargs = _slave_spread(svc.comm)

    svc.distribution(**master_template_kwargs)
    _log.debug("Setup tasks on rank '%d'" % svc.rank)
    barrier(svc.comm, "Setup tasks on rank '%d'" % svc.rank)

    # Collect tasks
    if svc.rank == MASTERRANK:
        _master_spread(svc.comm, svc.tasks)
    else:
        svc.tasks = _slave_spread(svc.comm)


def run_tasks(svc):
    """Make communicators for tasks and execute the work there"""
    # Based on initial dist, create the groups and communicators and map with work
    active_work = []
    wait_iter_sleep = 60  # run through all active work, then wait wait_iter_sleep seconds

    for wrk in svc.tasks:
        # # pass any existing previous work
        _log.debug("newcomm  for ranks %s for work %s: %s" % (wrk.ranks, wrk.options.name, wrk.type))
        newcomm = _make_comm_group(svc.comm, wrk.ranks)

        if newcomm == MPI.COMM_NULL:
            _log.debug('Skipping work setup for rank %d of this type %s' % (svc.rank, wrk.type))
            continue

        _log.debug('Setting up rank %d of this type %s' % (svc.rank, wrk.type))
        svc.tempcomm.append(newcomm)
        work = wrk.type(wrk.options, wrk.master_env)
        svc.log.debug("work %s begin" % (wrk.type.__name__))
        work.prepare_work_cfg()
        # # adding started work
        active_work.append(work)

    for act_work in active_work:
        svc.log.debug("work %s start" % (act_work.__class__.__name__))
        act_work.do_work_start()

    # # all work is started now
    while len(active_work):
        _log.debug("amount of active work %s" % (len(active_work)))
        for act_work in active_work:

            should_cleanup = act_work.do_work_wait()
            if should_cleanup:
                _log.debug("work %s stop" % (act_work.__class__.__name__))
                act_work.do_work_stop()
                _log.debug("work %s end" % (act_work.__class__.__name__))
                act_work.work_end()

                _log.debug("Removing %s from active_work" % act_work)
                active_work.remove(act_work)
        if len(active_work):
            _log.debug('Still %s active work left. sleeping %s seconds' % (len(active_work), wait_iter_sleep))
            time.sleep(wait_iter_sleep)
    _log.debug("No more active work left.")


class MpiService(object):
    """Basic mpi based service class"""
    def __init__(self, log=None):
        self.log = log
        if self.log is None:
            self.log = fancylogger.getLogger(name=self.__class__.__name__, fname=False)

        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

        self.tempcomm = []

        self.tasks = None

        #self.allnodes = _collect_nodes(self.comm, self.size)
        #self.topocom = _make_topology_comm(self.comm, self.allnodes, self.size, self.rank)

    def stop_service(self):
        """End all communicators"""
        self.log.debug("Stopping tempcomm")
        for comm in self.tempcomm:
            _stop_comm(comm)
        self.log.debug("Stopping self.comm")
        _stop_comm(self.comm)


    def distribution(self, **kwargs):
        """Master makes the distribution"""
        if self.rank == MASTERRANK:
            self.log.error("Redefine this in proper master service")
