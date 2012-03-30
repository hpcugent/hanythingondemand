from mpi4py import MPI

from hod.node import Node

MASTERRANK = 0

from vsc import fancylogger
fancylogger.setLogLevelDebug()

class MpiService:
    """Basic mpi based service class"""
    def __init__(self, initcomm=True, log=None):
        self.log = log
        if self.log is None:
            self.log = fancylogger.getLogger(self.__class__.__name__ + "_%d" % MPI.COMM_WORLD.rank)

        self.comm = None
        self.size = -1
        self.rank = -1

        self.masterrank = MASTERRANK

        self.barriercounter = 0

        self.stopwithbarrier = True

        self.allnodes = None ## Node info per rank
        self.topocomm = None
        self.tempcomm = []

        if initcomm:
            self.log.debug("Going to initialise the __init__ default communicators")
            self.init_comm()
        else:
            self.log.debug("No communicators initialised in __init__")


    def init_comm(self, origcomm=MPI.COMM_WORLD, startwithbarrier=False):
        self.log.debug('init_comm with origcomm %s and startwithbarrier %s' % (origcomm, startwithbarrier))
        try:
            self.comm = origcomm
            self.size = self.comm.Get_size()
            self.rank = self.comm.Get_rank()
        except:
            self.log.exception("Failed to initialise ")


        self.log.debug("Init with COMM_WORLD size %d rank %d masterrank %d communicator %s" % (self.size, self.rank, self.masterrank, self.comm))

        if startwithbarrier:
            self.barrier('Start ')

        ## init all nodes from original COMM_WORLD
        self.thisnode = Node()
        self.collect_nodes()

        self.dists = None

    def barrier(self, txt=''):
        """Perform MPI.barrier"""
        if not txt.endswith(' '):
            txt += " "
        self.log.debug("%swith barrier %d" % (txt, self.barriercounter))
        self.comm.barrier()
        self.log.debug("%swith barrier %d DONE" % (txt, self.barriercounter))
        self.barriercounter += 1

    def collect_nodes(self):
        """Collect local Node info and distribute it over all nodes"""
        descr = self.thisnode.go()
        self.log.debug("Got Node %s" % self.thisnode)

        self.allnodes = self.comm.alltoall([descr] * self.size)
        self.log.debug("Got allnodes %s" % (self.allnodes))

        ## TODO proper sanity check to see if all nodes have similar network (ie that the netmask of the selected index can reach the other indices)
        self.log.debug("Sanity check: do all nodes have same network adapters?")
        is_ok = True
        for intf in descr['network']:
            dev = intf[2]
            alldevs = [[y[2] for y in x['network']] for x in self.allnodes]
            for rnk in range(self.size):
                if not dev in alldevs[rnk]:
                    self.log.error("no dev %s found in alldevs %s of rank %s" % (dev, alldevs[rnk], rnk))
                    is_ok = False

        if is_ok:
            self.log.debug("Sanity check ok")
        else:
            self.log.error("Sanity check failed")

        self.make_topology_comm()

    def make_topology_comm(self):
        """Given the Node topology info, make communicator per dimension"""
        self.topocomm = [] ## self.comm not part of topocomm by default

        topo = self.allnodes[self.rank]['topology']
        dimension = len(topo) ## all nodes have same dimension (see sanity check)
        mykeys = [[]] * dimension

        ## sanity check
        ## - all topologies have same length
        foundproblem = False
        for n in range(self.size):
            sometopo = self.allnodes[n]['topology']
            if dimension == len(sometopo):
                for dim in range(dimension):
                    if topo[dim] == sometopo[dim]:
                        mykeys[dim].append(n) ## add the rank of somenode to the mykeys list in proper dimension
            else:
                self.log.error("Topology size of this Node %d does not match that of rank %d (size %d)" % (dimension, n, len(sometopo)))
                foundproblem = True

        if foundproblem:
            self.log.error("Found an irregularity. Not creating the topology communicators")
            return

        self.log.debug("List to determine keys %s" % mykeys)
        self.log.debug("Creating communicators per dimension (total dimension %d)" % dimension)
        for dimind in range(dimension):
            color = topo[dimind] ## identify newcomm 
            key = mykeys[dimind].index(self.rank) ## rank in newcomm
            newcomm = self.comm.Split(color, key) ## non-overlapping communicator 
            self.check_comm(newcomm, "Topologycomm dimensionindex %d color %d key %d" % (dimind, color, key))
            ## sanity check
            others = self.who_is_out_there(newcomm)
            self.log.debug("Others found %s; based on %s" % (others, mykeys[dimind]))
            if mykeys[dimind] == others:
                self.log.debug("Others %s in comm matches based input %s. Adding to topocomm." % (others, mykeys[dimind]))
                self.topocomm.append(newcomm)
            else:
                self.log.error("Others %s in comm don't match based input %s. Adding COMM_NULL to topocomm." % (others, mykeys[dimind])) ## TODO is adding COMM_NULL a good idea?
                self.topocomm.append(MPI.COMM_NULL)


    def who_is_out_there(self, comm):
        """Get all self.ranks of members of communicator"""
        others = comm.allgather(self.rank)
        self.log.debug("Are out there %s on comm %s" % (others, comm))
        return others

    def stop_comm(self, comm):
        """Stop a single communicator"""
        self.check_comm(comm, 'Stopping')

        if comm == MPI.COMM_NULL:
            self.log.debug("No disconnect COMM_NULL")
            return

        if self.stopwithbarrier:
            self.barrier('Stop')
        else:
            self.log.debug("Stop without barrier")

        if comm == MPI.COMM_WORLD:
            self.log.debug("No disconnect COMM_WORLD")
        else:
            self.log.debug("Stop disconnect")
            comm.Disconnect()

    def stop_service(self):
        """End all communicators"""
        if self.topocomm is not None:
            self.log.debug("Stopping topocomm")
            for comm in self.topocomm:
                self.stop_comm(comm)
        self.log.debug("Stopping tempcomm")
        for comm in self.tempcomm:
            self.stop_comm(comm)
        self.log.debug("Stopping self.comm")
        self.stop_comm(self.comm)

    def check_group(self, group, txt=''):
        """Report details about group"""
        if not txt.endswith(' '):
            txt += " "
        myrank = group.Get_rank()
        mysize = group.Get_size()
        self.log.debug("%sgroup %s size %d rank %d" % (txt, group, mysize, myrank))

    def check_comm(self, comm, txt=''):
        """Report details about communicator"""
        if not txt.endswith(' '):
            txt += " "
        if comm == MPI.COMM_NULL:
            self.log.debug("%scomm %s" % (txt, comm))
        else:
            myrank = comm.Get_rank()
            mysize = comm.Get_size()
            if comm == MPI.COMM_WORLD:
                self.log.debug("%scomm WORLD %s size %d rank %d" % (txt, comm, mysize, myrank))
            else:
                self.log.debug("%scomm %s size %d rank %d" % (txt, comm, mysize, myrank))


    def make_comm_group(self, ranks):
        """Make a new communicator based on set of ranks"""
        mygroup = self.comm.Get_group()
        self.log.debug("Creating newgroup using ranks %s from group %s" % (ranks, mygroup))
        newgroup = mygroup.Incl(ranks)
        self.check_group(newgroup, 'make_comm_group')

        newcomm = self.comm.Create(newgroup)
        self.check_comm(newcomm, 'make_comm_group')

        return newcomm

    def distribution(self):
        """Master makes the distribution"""
        if self.rank == MASTERRANK:
            self.log.error("Redefine this in proper master service")
        else:
            pass

    def spread(self):
        """bcast the master distribution"""
        if self.rank == self.masterrank:
            # master bcast to slaves
            self.comm.bcast(self.dists, root=self.masterrank)
            self.log.debug("Distributed dists %s from masterrank %s" % (self.dists, self.masterrank))
        else:
            self.dists = self.comm.bcast(root=self.masterrank)
            self.log.debug("Received dists %s from masterrank %s" % (self.dists, self.masterrank))

    def run_dist(self):
        """Make communicators for dists and execute the work there"""
        if self.dists is None:
            self.log.debug("No dists found. Running distribution and spread.")
            self.distribution()
            self.spread()


        """Based on initial dist, create the groups and communicators and map with work"""
        self.log.debug("Starting the distribution.")
        for wrk in self.dists:
            w_type = wrk[0]
            w_ranks = wrk[1]
            w_shared = None
            if len(wrk) == 3:
                w_shared = wrk[2]

            self.log.debug("newcomm for ranks %s for work %s" % (w_ranks, w_type))
            newcomm = self.make_comm_group(w_ranks)

            if newcomm == MPI.COMM_NULL:
                self.log.debug("No work %s for this rank %s" % (w_type, self.rank))
            else:
                self.tempcomm.append(newcomm)

                self.log.debug("work %s for ranks %s" % (w_type.__name__, w_ranks))
                tmp = w_type(w_ranks, w_shared)
                tmp.run(newcomm)


