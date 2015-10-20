.. _example_use_cases:

Example use cases
=================

A couple of example use cases are described below.

We assume that the ``hod`` command is readily available in the environment; if it is not by default, maybe you should
load a module first: see which ``hod`` or ``hanythingondemand`` modules are available via ``module avail``, and load one
of them using ``module load``.

.. contents:: :depth: 2
    :backlinks: none

.. _example_use_cases_common:

Common aspects
--------------

* configure HOD, by defining the HOD work directory and specifying which module should be loaded
  in the HOD job being submitted (see also :ref:`cmdline_create_options`)::

    $ export HOD_CREATE_HOD_MODULE=hanythingondemand/3.0.0-intel-2015b-Python-2.7.10
    $ export HOD_CREATE_WORKDIR=$VSC_SCRATCH/hod

* list available HOD 'distributions', to select a value to specify to ``--dist``::

    $ hod dists
    HBase-1.0.2
    Hadoop-2.3.0-cdh5.0.0
    Hadoop-2.5.0-cdh5.3.1-gpfs
    Hadoop-2.5.0-cdh5.3.1-native
    Hadoop-on-lustre2
    IPython-notebook-3.2.1

.. _example_use_cases_interactive_hadoop:

Interactively using an HOD cluster (Hadoop)
-------------------------------------------

To interactively use an HOD cluster, you should (i) create an HOD cluster, (ii) connect to it once it is up and running.

In the example below, we create a Hadoop HOD cluster, connect to it, and run the standard WordCount example Hadoop job
(see https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html#Example:_WordCount_v1.0).

* create a Hadoop HOD cluster labelled ``hod_hadoop``::

    $ hod create --dist Hadoop-2.5.0-cdh5.3.1-native --label hod_hadoop

    Submitting HOD cluster with label 'hod_hadoop'...
    Job submitted: Jobid 12345.master15.delcatty.gent.vsc state Q ehosts 

* check HOD cluster status ('``Q``' for queued, '``R``' for running)::

    $ hod list

    Cluster label	Job ID                         	    State	Hosts                   
    hod_hadoop   	12345.master15.delcatty.gent.vsc	Q 

    $ hod list

    Cluster label	Job ID                         	    State	Hosts                   
    hod_hadoop   	12345.master15.delcatty.gent.vsc	R    	node2001.delcatty.gent.vsc

* connect to the running cluster::

    $ hod connect hod_hadoop

    Connecting to HOD cluster with label 'hod_hadoop'...
    Job ID found: 12345.master15.delcatty.gent.vsc
    HOD cluster 'hod_hadoop' @ job ID 12345.master15.delcatty.gent.vsc appears to be running...
    Setting up SSH connection to node2001.delcatty.gent.vsc...
    Welcome to your hanythingondemand cluster (label: hod_hadoop)

    Relevant environment variables:
    HADOOP_CONF_DIR=/user/scratch/gent/vsc400/vsc40000/hod/hod/12345.master15.delcatty.gent.vsc/vsc40000.node2001.delcatty.os.26323/conf
    HADOOP_HOME=/apps/gent/CO7/haswell-ib/software/Hadoop/2.5.0-cdh5.3.1-native/share/hadoop/mapreduce
    HOD_LOCALWORKDIR=/user/scratch/gent/vsc400/vsc40000/hod/hod/12345.master15.delcatty.gent.vsc/vsc40000.node2001.delcatty.os.26323

    List of loaded modules:
    Currently Loaded Modulefiles:
      1) cluster/delcatty(default)        2) Java/1.7.0_76                  3) Hadoop/2.5.0-cdh5.3.1-native

* run Hadoop WordCount example

  * change to local work directory of this cluster::

        $ cd $HOD_LOCALWORKDIR

  * download example input file for wordcount::

        $ curl http://www.gutenberg.org/files/98/98.txt -o tale-of-two-cities.txt

  * build ``WordCount.jar``::

        $ cp $HOME/WordCount.java .
        $ javac -classpath $(hadoop classpath) WordCount.java
        $ jar cf WordCount.jar WordCount*.class

  * run ``WordCount`` Hadoop example::

        $ hadoop jar WordCount.jar WordCount tale-of-two-cities.txt wordcount.out
        # (output omitted)

  * query result::

        $ grep ^city wordcount.out/part-r-00000 
        city	20
        city,	9
        city.	5

.. note:: ``screen``

.. _example_use_cases_batch_hadoop:

Running a batch script on an HOD cluster (Hadoop)
-------------------------------------------------

.. _example_use_cases_ipython:

Connecting to an IPython notebook running on an HOD cluster
-----------------------------------------------------------

