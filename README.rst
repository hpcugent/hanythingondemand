hanythingondemand (HOD for short)
=================================

Documentation is available at `Read the
Docs <http://hod.readthedocs.org>`__

|Build Status|

Goal
----

HOD is a set of scripts to start services, for example a Hadoop cluster,
from within another resource management system (i.e. Torque/PBS). As
such, it allows traditional users of HPC systems to experiment with
Hadoop or use it as a production setup if there is no dedicated setup
available.

Hadoop is not the only software supported. HOD can also create HBase
databases, IPython notebooks, and set up a Spark environment.

Benefits
--------

There are two main benefits:

1. Users can run jobs on a traditional batch cluster. This is good for
   small to medium Hadoop jobs where the framework is used but having a
   'big data' cluster isn't required. At this point the performance
   benefits of a parallel file system outweigh the 'share nothing'
   architecture of a HDFS style file system.

2. Users from different groups can run whichever version of Hadoop they
   like. This removes the need for painful upgrades to running Yarn
   clusters and hoping all users' jobs are backwards compatible.

History
-------

Hadoop used to ship it's own HOD (Hadoop On Demand) but it was not
maintained and only supported Hadoop without tuning. The HOD code that
was shipped with Hadoop 1.0.0 release was buggy to say the least. An
attempt was made to make it work on the UGent HPC infrastructure, and
although a working Hadoop cluster was realised, it was a nightmare to
extend it's functionality. At that point (April 2012), hanythingondemand
was started to be better maintainable and support more tuning and
functionality out of the box. For example, HBase was a minimum
requirement. Hence, why Hadoop on Demand became 'Hanything'. Apart from
the acronym 'HOD' nothing of Hadoop On Demand was reused.

More on the history of Hadoop On Demand can be found in section 2 of
`this paper on Yarn
(PDF) <http://www.cs.cmu.edu/~garth/15719/papers/yarn.pdf>`__

How does it work?
-----------------

hanythingondemand works by launching an MPI job which uses the reserved
nodes as a cluster-in-a-cluster. These nodes then have the various
Hadoop services started on them. Users can launch a job at startup
(batch mode) or login to worker nodes (using the ``hod connect``
command) where they can interact with their services.

Prerequisites
-------------

-  A cluster using
   `Torque <http://www.adaptivecomputing.com/products/open-source/torque/>`__.
-  `environment-modules <http://modules.sourceforge.net/>`__ to manage
   the environment

The rest of the requirements can be installed using
`EasyBuild <https://github.com/hpcugent/easybuild>`__:

-  Python and various libraries.
-  `mpi4py <http://mpi4py.scipy.org/>`__
-  eg. on fedora ``yum install -y mpi4py-mpich2``
-  If you build this yourself, you will probably need to set the $MPICC
   environment variable.
-  `vsc-base <https://github.com/hpcugent/vsc-base>`__ - Used for
   command line parsing.
-  `vsc-mympirun <https://github.com/hpcugent/vsc-mympirun>`__ -
   Used for setting up the MPI job.
-  `pbs_python <https://oss.trac.surfsara.nl/pbs_python>`__ - Used
   for interacting with the PBS (aka Torque) server.
-  `netifaces <https://pypi.python.org/pypi/netifaces>`__
-  `netaddr <https://pypi.python.org/pypi/netaddr/>`__
-  Java
-  Oracle JDK or OpenJDK - both installable with Easybuild
-  Hadoop binaries
-  eg. the `Cloudera distribution
   versions <http://archive.cloudera.com/cdh4/cdh/4/>`__ (used to test
   HOD)

Example use cases:
------------------

Creating an HOD cluster:
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

    # submits a job to start a Hadoop cluster on 16 nodes
    $ hod create --dist Hadoop-2.3.0-cdh5.0 -n16 --label my-cluster

    ### Connect to your new cluster.
    $ hod connect my-cluster

    ### Then, in your session, you can run your hadoop jobs:
    $ hadoop jar somejob.jar SomeClass arg1 arg2

‘Set it and forget it’ batch jobs:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

    # Run a batch job on 1 node:
    $ hod batch --dist Hadoop-2.3.0-cdh5.0 --label my-cluster --script=my-script.sh

.. |Build Status| image:: https://travis-ci.org/hpcugent/hanythingondemand.svg?branch=master
   :target: https://travis-ci.org/hpcugent/hanythingondemand
