# hanythingondemand  (HOD for short)
[![Build
Status](https://travis-ci.org/ehiggs/hanythingondemand.svg?branch=autoconf)](https://travis-ci.org/ehiggs/hanythingondemand)

## Goal
hanythingondemand is a set of scripts to start a Hadoop cluster from within
another resource management system (i.e. Torque/PBS). It allows traditional
users of HPC systems to experiment with Hadoop or use it as a production setup
if there is no dedicated setup available.

## History
Hadoop used to ship it's own HOD (Hadoop On Demand) but it was not maintained
and only supported Hadoop without tuning. The HOD code that was shipped with
Hadoop 1.0.0 release was buggy to say the least. An attempt was made to make it
work on UGent HPC infrastructure, and although a working Hadoop cluster was
realised, it was a nightmare to extend it's functionality. At that point (April
2012), hanythingondemand was started to be better maintainable and support more
tuning and functionality out of the box. For example, HBase was a minimum
requirement. Hence, why Hadoop on Demand became 'Hanything'. Apart from the
acronym HOD nothing of Hadoop On Demand was reused.

More on the history of HOD can be found in section 2 of [this paper on Yarn
(PDF)](http://www.cs.cmu.edu/~garth/15719/papers/yarn.pdf)

## How does it work?
hanythingondemand works by launching an MPI job which uses the reserved nodes 
as a cluster-in-a-cluster. These nodes then have the various Hadoop services
started on them. Users can launch a job at startup or login to worker node
and attach to a screen session where they can interact with their services.

## Prerequisites
* A cluster using [Torque](http://www.adaptivecomputing.com/products/open-source/torque/).
* [environment-modules](http://modules.sourceforge.net/) to manage the environment
 * This is optional if everything is setup and usable (eg. `PATH`, `JAVA_HOME`, `PYTHONPATH`)
* Python and various libraries.
 * [`mpi4py`](http://mpi4py.scipy.org/) 
  * eg. on fedora `yum install -y mpi4py-mpich2`
  * If you build this yourself, you will probably need to set the MPICC
    environment variable.
 * [`vsc-base`](https://github.com/hpcugent/vsc-base) - Used for command line parsing.
 * [`vsc-mympirun`](https://github.com/hpcugent/vsc-mympirun) - Used for setting up the MPI job.
 * [`pbs_python`](https://oss.trac.surfsara.nl/pbs_python) - Used for interacting with the PBS (aka Torque) server.
* [Easybuild](https://github.com/hpcugent/easybuild) - we use Easybuild for installing software and hanythingondemand isn't tested without it.
* Java 
 * Oracle JDK or OpenJDK - both installable with Easybuild
* Hadoop binaries
 * eg. the [Cloudera distribution versions](http://archive.cloudera.com/cdh4/cdh/4/) (used to test HOD)


## Usage
### On a cluster
 Use `hod_pbs.py` for pbs support
### On localhost
 * Set the environment
  * Create a small script so that the environment is setup
  * eg. on yum based distributions
   * Download [hadoop-2.0.0-cdh4.4.0.tar.gz](http://archive.cloudera.com/cdh4/cdh/4/) in `$HOME/hadoop/cdh4.4.0` and unpack.
   * Install mpi4py and java: `yum install -y mpi4py-mpich2 java-1.6.0-openjdk`
   * Install hanythingondemand in $HOME/hod
   * Sourcing the following script will setup the correct environment.
 
```shell
# Create a Hadoop cluster on 16 nodes.
hod_pbs.py --config-conf=$EBROOTHANYTHINGONDEMAND/etc/hod/Hadoop-2.3.0-cdh5.0/hod.conf --action-create -n16

# Create a Hadoop cluster on 16 nodes with local overrides from your own hod.conf file
hod_pbs.py --config-conf=$EBROOTHANYTHINGONDEMAND/etc/hod/Hadoop-2.3.0-cdh5.0/hod.conf,./hod.conf --action-create -n16


## Wiki
For more documentation, check the wiki
[here](http://github.com/hpcugent/hanythingondemand/wiki/)
