.. _cmdline:

Command line interface
======================

This page provides an overview of the hanythingondemand command line interface.

.. note:: This only applies to hanythingondemand version 3 and newer; older versions provided a significantly different
          command line interface.

.. contents:: :depth: 3

.. _cmdline_hod:

``hod`` command
---------------

The main hanythingondemand command is a Python script named ``hod``, and implements the top-level
command line interface that discriminates between the various subcommands.

Running ``hod`` without arguments is equivalent to ``hod --help``, and results in basic usage information being printed:

.. FIXME generate this
.. code::

    $ hod
    hanythingondemand version 3.2.0 - Run services within an HPC cluster
    usage: hod <subcommand> [subcommand options]
    Available subcommands (one of these must be specified!):
        batch           Submit a job to spawn a cluster on a PBS job controller, run a job script, and tear down the cluster when it's done
        clean           Remove stale cluster info.
        clone           Write hod configs to a directory for editing purposes.
        connect         Connect to a hod cluster.
        create          Submit a job to spawn a cluster on a PBS job controller
        destroy         Destroy an HOD cluster.
        dists           List the available distributions
        genconfig       Write hod configs to a directory for diagnostic purposes
        help-template   Print the values of the configuration templates based on the current machine.
        list            List submitted/running clusters
        relabel         Change the label of an existing job.

.. _cmdline_hod_options:

General ``hod`` command line options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _cmdline_hod_help:

``hod [subcommand] --help``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Print usage information and supported subcommands along with a short help message for each of them, or usage information
and available options for the specified subcommand.


.. .. _cmdline_hod_scheduler:

.. ``hod --scheduler``
.. ^^^^^^^^^^^^^^^^^^^

.. Specify which scheduler to use; if no interface is specified, a list of available schedulers is printed.

.. .. note:: For now, only ``PBS`` is supported.


.. -----------
.. SUBCOMMANDS
.. -----------

.. _cmdline_hod_subcommands:

``hod`` subcommands
-------------------

The ``hod`` command provides a number of subcommands, which correspond to different actions.

An overview of the available subcommands is available via ``hod --help`` (see :ref:`cmdline_hod`).

More details on a specific subcommand are available via ``hod <subcommand> --help``.

Available subcommands:

* :ref:`cmdline_batch`
* :ref:`cmdline_clean`
* :ref:`cmdline_clone`
* :ref:`cmdline_connect`
* :ref:`cmdline_create`
* :ref:`cmdline_destroy`
* :ref:`cmdline_dists`
* :ref:`cmdline_genconfig`
* :ref:`cmdline_helptemplate`
* :ref:`cmdline_list`
* :ref:`cmdline_relabel`


.. _cmdline_batch:

``hod batch --script=<script-name>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a cluster and run the script. Upon completion of the script, the cluster will be stopped.

Next to ``--script`` (which is mandatory with ``batch``), all configuration options supported for ``create`` are
also supported for ``batch``, see :ref:`cmdline_create_options`.
When used with ``batch``, these options can also be specified via ``$HOD_BATCH_*``.

Jobs that have completed will remain in the output of ``hod list`` with a job id of ``<job-not-found>``
until ``hod clean``  is run (see :ref:`cmdline_clean`), or until the cluster is destroyed using ``hod destroy``
(see :ref:`cmdline_destroy`).

.. note:: ``--hod-module``, ``--workdir``, and either ``--hodconf`` or ``--dist`` **must** be specified.


.. _cmdline_clean:

``hod clean``
~~~~~~~~~~~~~

Remove cluster info directory for clusters that are no longer available,
i.e. those marked with ``<job-not-found>`` in the output of ``hod list``.


.. _cmdline_clone:

``hod clone <dist-name> <destination>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone a dist for use editing purposes. If there is a provided dist that is almost what is required for some work, users 
can clone it and edit the files.

.. _cmdline_connect:

``hod connect <cluster-label>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. ssh + set up environment (screen no longer needed!)

Connect to an existing hanythingondemand cluster, and set up the environment to use it.

This basically corresponds to logging in to the cluster head node using SSH and sourcing the cluster information script
that was created for this cluster (``$HOME/.config/hod.d/<label>/env``).


.. _cmdline_create:

``hod create``
~~~~~~~~~~~~~~

Create a hanythingondemand cluster, with the specified label (optional) and cluster configuration file (required).

.. TODO the number part

The configuration file can be a filepath, or one of the included cluster configuration files (see :ref:`cmdline_dists`).

Jobs that have completed will remain in the output of ``hod list`` with a job id of ``<job-not-found>`` until ``hod clean`` 
is run (see :ref:`cmdline_clean`), or until the cluster is destroyed using ``hod destroy`` (see :ref:`cmdline_destroy`).

.. note:: ``--hod-module``, ``--workdir``, and either ``--hodconf`` or ``--dist`` must be specified.


.. _cmdline_create_options:

Configuration options for ``hod create``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _cmdline_create_options_hod_module:

``hod create --hod-module <module name>``
+++++++++++++++++++++++++++++++++++++++++

**must be specified**

Specify the ``hanythingondemand`` module that must be loaded in the job that is submitted for the HOD cluster;
can also be specified via ``$HOD_CREATE_HOD_MODULE``.


.. _cmdline_create_options_workdir:

``hod create --workdir <path>``
+++++++++++++++++++++++++++++++

**must be specified**

Specify the top-level working directory to use; can also be specified via ``$HOD_CREATE_WORKDIR``.


.. _cmdline_create_options_hodconf:

``hod create --hodconf <path>``
+++++++++++++++++++++++++++++++

**either** ``--dist`` **or this must be specified**

Specify location of cluster configuration file; can also be specified via ``$HOD_CREATE_HODCONF``.


.. _cmdline_create_options_dist:

``hod create --dist <dist>``
++++++++++++++++++++++++++++

**either** ``--hodconf`` **or this must be specified**

Specify one of the included cluster configuration file to be used (see also :ref:`cmdline_dists`);
can also be specified via ``$HOD_CREATE_DIST``.


.. _cmdline_create_options_label:

``hod create --label <label>``
++++++++++++++++++++++++++++++

Specify label for this cluster. If not label is specified, the job ID will be used as a label;
can also be specified via ``$HOD_CREATE_LABEL``.

The label can be used to later connect to the cluster while it is running (see :ref:`cmdline_connect`).


.. _cmdline_create_options_modulepaths:

``hod create --modulepaths <paths>``
++++++++++++++++++++++++++++++++++++

Add additional locations for modules that need to be loaded (see :ref:`cmdline_create_options_modules`).

Can also be specified via ``$HOD_CREATE_MODULEPATHS``.


.. _cmdline_create_options_modules:

``hod create --modules <module names>``
+++++++++++++++++++++++++++++++++++++++

Add modules to the dist so each node has access to them. If code submitted to
the cluster requires a particular module, it should be added with this option.
For example, if an IPython notebook plans to use Python modules on the worker
kernels (or through Spark) they will need to be added here.

Can also be specified via ``$HOD_CREATE_MODULES``.



.. _cmdline_create_options_job:

``hod create --job-*``
++++++++++++++++++++++

The resources being requested for the job that is submitted can be controlled via the available ``--job`` options,
see :ref:`cmdline_job_options`.


.. _cmdline_destroy:

``hod destroy <cluster-label>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destroy the HOD cluster with the specified label.

This involves deleting the job, and removing the working directory and cluster info directory
(``$HOME/.config/hod.d/<label>``) corresponding to this cluster, if they are still in place.

In case the cluster is currently *running*, confirmation will be requested.


.. _cmdline_dists:

``hod dists``
~~~~~~~~~~~~~

Print a list of available cluster configurations ('*distributions*'),
along with the list of modules that correspond to each of them.

See for example :ref:`example_use_cases_common_available_dists`.

.. _cmdline_genconfig:

``hod genconfig``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate hanythingondemand cluster configuration files to the working directory for diagnostic purposes.

The working directory can be specified using ``--workdir`` or via ``$HOD_GENCONFIG_WORKDIR``.


.. _cmdline_helptemplate:

``hod help-template``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. FIXME machine?

Print the values for the configuration templates based on the current machine.


.. _cmdline_list:

``hod list``
~~~~~~~~~~~~

.. TODO enhance output?

Print a list of existing clusters, and their state ('``queued``' or '``running``').

Jobs that have completed running will remain in the list with ``<job-not-found>`` until
``hod clean`` is run (see :ref:`cmdline_clean`), or until the HOD cluster is destroyed using ``hod destroy``
(see :ref:`cmdline_destroy`).


.. _cmdline_relabel:

``hod relabel <old-label> <new-label>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change the label for a hod cluster that is queued or running.


.. -----------
.. JOB OPTIONS
.. -----------

.. _cmdline_job_options:

``--job`` options for ``hod create`` / ``hod batch``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``create`` and ``batch`` subcommands accept the following options to specify requested job resources.

These can also be specified via ``$HOD_BATCH_JOB_*`` (for ``hod batch``) or ``$HOD_CREATE_JOB_*`` (for ``hod create``).


.. _cmdline_job_options_mail:

``--job-mail``/``-m <string>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Send a mail when the cluster has started (``b`` for '*begin*'), stopped (``e`` for '*ended*') or got aborted (``a``).

For example, using ``-m a`` will result in receiving a mail whn the cluster has started running.

.. _cmdline_job_options_mail_others:

``--job-mailothers``/``-M <main addresses>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

List of other mail adresses to send mails to.

.. _cmdline_job_options_name:

``--job-name``/``-N <name>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specify the name for the job that will be submitted.

.. _cmdline_job_options_nodes:

``--job-nodes``/``-n <int>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The number of (full) workernodes to request for the job being submitted (default: 1).


.. _cmdline_job_options_ppn:

``--job-ppn <int>``
^^^^^^^^^^^^^^^^^^^

The number of cores per workernode to request; by default: ``-1``, i.e. full workernodes (request all available cores).


.. _cmdline_job_options_reservation:

``--job-reservation <reservation ID>``

Reservation ID to submit job into (equivalent with using ``-W x=FLAGS:ADVRES:<reservation ID>`` with ``qsub``).


.. _cmdline_job_options_queue:

``--job-queue``/``-q <int>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Name of job queue to submit to (default: none specified).


.. _cmdline_job_options_walltime:

``--job-walltime``/``-l <int>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Number of hours of walltime to request (default: 48).
