#!/usr/bin/env python

from hod.mpiservice import MpiService, MASTERRANK

from hod.work.work import TestWorkA, TestWorkB
from hod.work.mapred import Mapred
from hod.work.hdfs import Hdfs

from hod.config.customtypes import HostnamePort

from vsc import fancylogger
fancylogger.setLogLevelDebug()


class Master(MpiService):
    """Basic Master"""

    def distribution(self):
        """Master makes the distribution"""
        ## example part one on half one, part 2 on second half (make sure one is always started)
        self.dists = []

        allranks = range(self.size)
        lim = self.size / 2
        self.dists.append([TestWorkA, allranks[:max(lim, 1)]]) ## for lim == 0, make sure TestWorkA is started
        self.dists.append([TestWorkB, allranks[lim:]])

class Slave(MpiService):
    """Basic Slave"""

class HadoopMaster(MpiService):
    """Basic Master Hdfs and MR1"""

    def distribution(self):
        """Master makes the distribution"""
        ## example part one on half one, part 2 on second half (make sure one is always started)
        self.dists = []

        ## 4 things to start
        ## HDFS config
        ##   nameserver (and broadcast this to further services)
        ##   datanodes
        ## MR1 config
        ##   jobtracker
        ##   tasktracker

        network_index = self.select_network()

        ## namenode on rank 0, jobtracker of last one
        nn_rank, hdfs_ranks = self.select_hdfs_ranks()
        nn_param = [HostnamePort("%s:8020" % self.allnodes[nn_rank]['network'][network_index][0]),
                  'Namenode on rank %s network_index %s' % (nn_rank, network_index)]

        jt_rank, mapred_ranks = self.select_mapred_ranks()
        jt_param = [HostnamePort("%s:9000" % self.allnodes[jt_rank]['network'][network_index][0]),
                    'Jobtracker on rank %s network_index %s' % (jt_rank, network_index)]


        shared = {'params':{'fs.default.name':nn_param }}
        self.dists.append([Hdfs, hdfs_ranks, shared])


        shared['params'].update({'mapred.job.tracker':jt_param})
        self.dists.append([Mapred, mapred_ranks, shared])


    def select_network(self):
        """Given the network info collected in self.allnodes[x]['network'], return the index of the network to use"""

        index = 0 ## the networks are ordered by default, use the first one


        self.log.debug("using network index %s" % index)
        return index

    def select_hdfs_ranks(self):
        """return namenode rank and all datanode ranks"""
        allranks = range(self.size)
        nn_rank = allranks[0]
        self.log.debug("Simple hdfs distribution: nn is first of allranks and all ranks are datanode: %s, %s" % (nn_rank, allranks))
        return nn_rank, allranks

    def select_mapred_ranks(self):
        """return jobtracker rank and all tasktracker ranks"""
        allranks = range(self.size)
        jt_rank = allranks[-1]
        self.log.debug("Simple mapred distribution: jt is last of allranks and all ranks are tasktracker: %s , %s" % (jt_rank, allranks))
        return jt_rank, allranks

if __name__ == '__main__':
    from mpi4py import MPI

    if MPI.COMM_WORLD.rank == MASTERRANK:
        serv = HadoopMaster()
    else:
        serv = Slave()

    try:
        import time

        time.sleep(1)

        serv.run_dist()

        serv.stop_service()
    except:
        serv.log.exception("Main failed")


