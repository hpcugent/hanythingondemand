.. _example_use_cases:

Example use cases
=================

A couple of example use cases are described below.

We assume that the ``hod`` command is readily available in the environment; if it is not by default, maybe you should
load a module first: see which ``hod`` or ``hanythingondemand`` modules are available via ``module avail``, and load one
of them using ``module load``.

To check, just run ``hod`` without arguments, which should produce basic usage information (see :ref:`cmdline_hod`).

.. contents:: :depth: 2
    :backlinks: none

.. _example_use_cases_common:

Common aspects
--------------

.. _example_use_cases_common_configuring_hod:

Configuring HOD
~~~~~~~~~~~~~~~


You can/should configure HOD by defining the HOD work directory and specifying which module should be loaded
in the HOD job being submitted (see also :ref:`cmdline_create_options`)::

    # for 'hod batch'
    $ export HOD_BATCH_HOD_MODULE=hanythingondemand/3.0.0-intel-2015b-Python-2.7.10
    $ export HOD_BATCH_WORKDIR=$VSC_SCRATCH/hod
    # for 'hod create'
    $ export HOD_CREATE_HOD_MODULE=hanythingondemand/3.0.0-intel-2015b-Python-2.7.10
    $ export HOD_CREATE_WORKDIR=$VSC_SCRATCH/hod

The examples below will assume that this configuration is in place already.

.. _example_use_cases_common_available_dists:

Available distributions
~~~~~~~~~~~~~~~~~~~~~~~

To get an overview of readily available HOD distributions, to select a value to specify to ``--dist``,
use ``hod dists``::

    $ hod dists
    HBase-1.0.2
    Hadoop-2.3.0-cdh5.0.0
    Hadoop-2.5.0-cdh5.3.1-gpfs
    Hadoop-2.5.0-cdh5.3.1-native
    Hadoop-2.6.0-cdh5.4.5-native
    Hadoop-on-lustre2
    IPython-notebook-3.2.1

.. _example_use_cases_interactive_hadoop:

Interactively using a Hadoop cluster
------------------------------------

To interactively use an HOD cluster, you should

(i) create an HOD cluster, using ``hod create``
(ii) connect to it once it is up and running, using ``hod connect``
(iii) execute your commands

See the example below for more details; basic usage information for ``hod create`` is available at :ref:`cmdline_create`.

.. _example_use_cases_interactive_hadoop_screen:

Using ``screen``
~~~~~~~~~~~~~~~~

To interactively start commands that may require some time to finish, we strongly recommended starting a
so-called *screen* session after connecting to the HOD cluster.

Basic usage:

* to start a screen session, simply the ``screen`` command; to specify a name for the session,
  use ``screen -S <name>``
* to get an overview of running screen sessions, use ``screen -ls``
* to detach from a screen session, with the option to later reattach to it, us the ``Ctrl-A-D`` key combination.
* to *end* a screen session, simply type ``exit`` (no reattaching possible later!)
* to reconnect to a screen session, use ``screen -r <name>``; or simply use ``screen -r`` if there's only one
  running screen session

More information about ``screen`` is available at http://www.gnu.org/software/screen/manual/screen.html.

.. _example_use_cases_interactive_hadoop_example:

Example: Hadoop WordCount
~~~~~~~~~~~~~~~~~~~~~~~~~

In the example below, we create a Hadoop HOD cluster, connect to it, and run the `standard WordCount example Hadoop job
<https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html#Example:_WordCount_v1.0>`_.

* create a Hadoop HOD cluster labelled ``hod_hadoop``::

    $ hod create --dist Hadoop-2.5.0-cdh5.3.1-native --label hod_hadoop

    Submitting HOD cluster with label 'hod_hadoop'...
    Job submitted: Jobid 12345.master15.delcatty.gent.vsc state Q ehosts 

* check the status of the HOD cluster ('``Q``' for queued, '``R``' for running)::

    $ hod list

    Cluster label	Job ID                         	    State	Hosts                   
    hod_hadoop   	12345.master15.delcatty.gent.vsc	Q 

    ...

    $ hod list

    Cluster label	Job ID                         	    State	Hosts                   
    hod_hadoop   	12345.master15.delcatty.gent.vsc	R    	node2001.delcatty.gent.vsc

* connect to the running HOD cluster::

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

  * build ``WordCount.jar`` (*note:* assumes that ``$HOME/WordCount.java`` is available)::

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

.. _example_use_cases_batch_hadoop:

Running a batch script on a Hadoop cluster
------------------------------------------

Since running a pre-defined set of commands is a common pattern, HOD also supports an alternative to creating an HOD
cluster and using it interactively.

Via ``hod batch``, a script can be provided that should be executed on an HOD cluster. In this mode, HOD will:

* start an HOD cluster with the specified configuration (working directory, HOD distribution, etc.)
* execute the provided script
* automatically destroy the cluster once the script has finished running

This alleviates the need to wait until a cluster effectively starts running and entering the commands interactively.

See also the example below; basic usage information for ``hod batch`` is available at :ref:`cmdline_batch`.

Example: Hadoop WordCount
~~~~~~~~~~~~~~~~~~~~~~~~~

The classic Hadoop WordCount can be run using the following script (``wordcount.sh``) on an HOD cluster::

    #!/bin/bash

    # move to (local) the local working directory of HOD cluster on which this script is run
    export WORKDIR=$VSC_SCRATCH/$PBS_JOBID
    mkdir -p $WORKDIR
    cd $WORKDIR

    # download example input file for wordcount
    curl http://www.gutenberg.org/files/98/98.txt -o tale-of-two-cities.txt

    # build WordCount.jar (note: assumes that ``$HOME/WordCount.java`` is available)
    cp $HOME/WordCount.java .
    javac -classpath $(hadoop classpath) WordCount.java
    jar cf WordCount.jar WordCount*.class

    # run WordCount Hadoop example
    hadoop jar WordCount.jar WordCount tale-of-two-cities.txt wordcount.out

    # copy results
    cp -a wordcount.out $HOME/$PBS_JOBNAME.$PBS_JOBID

.. note:: No modules need to be loaded in order to make sure the required software is available (i.e., Java, Hadoop).
          Setting up the working environment in which the job will be run is done right after starting the HOD cluster.

          To check which modules are/will be available, you can use ``module list`` in the script you supply to
          ``hod batch`` or check the details of the HOD distribution you use via :ref:`cmdline_clone`.


To run this script on a Hadoop cluster, we can submit it via ``hod batch``::

    $ hod batch --dist Hadoop-2.5.0-cdh5.3.1-native --script $PWD/wordcount.sh --label wordcount
    Submitting HOD cluster with label 'wordcount'...
    Job submitted: Jobid 12345.master15.delcatty.gent.vsc state Q ehosts

    $ hod list
    Cluster label	Job ID                         	    State	Hosts
    wordcount    	12345.master15.delcatty.gent.vsc	R    	node2001.delcatty.gent.vsc

Once the script is finished, the HOD cluster will destroy itself, and the job running it will end::

    $ hod list
    Cluster label	Job ID                         	    State          	Hosts
    wordcount    	12345.master15.delcatty.gent.vsc	<job-not-found>	<none>

Hence, the results should be available (see the ``cp`` at the end of the submitted script)::

    $ ls $HOME/HOD_wordcount.12345.master15.delcatty.gent.vsc
    total 416
    -rw-r--r-- 1 example  example  210041 Oct 22 13:34 part-r-00000
    -rw-r--r-- 1 example  example       0 Oct 22 13:34 _SUCCESS

    $ grep ^city $HOME/HOD_wordcount.12345.master15.delcatty.gent.vsc/part-r-00000
    city	20
    city,	9
    city.	5

.. note:: To get an email when the HOD cluster is started/stopped, use the ``-m`` option,
          see :ref:`cmdline_job_options_mail`.

.. _example_use_cases_ipython:

Connecting to an IPython notebook running on an HOD cluster
-----------------------------------------------------------

Running an IPython notebook on an HOD cluster is as simple as creating an HOD cluster using the appropriate
distribution, and then connecting to the IPython notebook over an SSH tunnel.

For example:

* create HOD cluster using an IPython HOD distribution::

    $ hod create --dist IPython-notebook-3.2.1 --label ipython_example
    Submitting HOD cluster with label 'ipython_example'...
    Job submitted: Jobid 12345.master15.delcatty.gent.vsc state Q ehosts

* determine head node of HOD cluster::

    $ hod list
    Cluster label	Job ID                         	    State	Hosts
    ipython_example 12345.master15.delcatty.gent.vsc	R    	node2001.delcatty.gent.vsc

* connect to IPython notebook by pointing your web browser to http://localhost:8888, using a SOCKS proxy over
  an SSH tunnel to the head node ``node2001.delcatty.gent.vsc`` (see :ref:`connecting_to_web_uis` for detailed
  information)
