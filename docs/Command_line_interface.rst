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
    hanythingondemand version 3.0.0 - Run services within an HPC cluster
    usage: hod <subcommand> [subcommand options]
    Available subcommands (one of these must be specified!):
        create          Submit a job to spawn a cluster on a PBS job controller
        batch           Submit a job to spawn a cluster on a PBS job controller, run a job script, and tear down the cluster when it's done
        list            List submitted/running clusters
        dists           List the available distributions
        help-template   Print the values of the configuration templates based on the current machine.
        genconfig       Write hod configs to a directory for diagnostic purposes
        connect         Connect to a hod cluster.
        clean           Remove stale cluster info.

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

Known subcommands:

* :ref:`cmdline_create`
* :ref:`cmdline_batch`
* :ref:`cmdline_list`
* :ref:`cmdline_dists`
* :ref:`cmdline_helptemplate`
* :ref:`cmdline_genconfig`
* :ref:`cmdline_connect`

.. _cmdline_create:

``hod create``
~~~~~~~~~~~~~~

Create a hanythingondemand cluster, with the specified label (optional) and cluster configuration file (required).

.. TODO the number part

The configuration file can be a filepath, or one of the included cluster configuration files (see :ref:`cmdline_dists`).

Jobs that have completed will remain in the output of ``hod list`` with a job id of ``<no-job>`` until ``hod clean`` 
is run (see :ref:`cmdline_clean`).

.. note:: ``--hod-module``, ``--workdir``, and either ``--hodconf`` or ``--dist`` must be specified.


.. _cmdline_create_options:

Configuration options for ``hod create``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _cmdline_create_options_hod_module:

``hod create --hod-module <module name>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**must be specified**

Specify the ``hanythingondemand`` module that must be loaded in the job that is submitted for the HOD cluster;
can also be specified via ``$HOD_CREATE_HOD_MODULE``.


.. _cmdline_create_options_workdir:

``hod create --workdir <path>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**must be specified**

Specify the top-level working directory to use; can also be specified via ``$HOD_CREATE_WORKDIR``.


.. _cmdline_create_options_hodconf:

``hod create --hodconf <path>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**either** ``--dist`` **or this must be specified**

Specify location of cluster configuration file; can also be specified via ``$HOD_CREATE_HODCONF``.


.. _cmdline_create_options_dist:

``hod create --dist <dist>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**either** ``--hodconf`` **or this must be specified**

Specify one of the included cluster configuration file to be used (see also :ref:`cmdline_dists`);
can also be specified via ``$HOD_CREATE_DIST``.


.. _cmdline_create_options_label:

``hod create --label <label>``
++++++++++++++++++++++++++++++

Specify label for this cluster. If not label is specified, the job ID will be used as a label;
can also be specified via ``$HOD_CREATE_LABEL``.

The label can be used to later connect to the cluster while it is running (see :ref:`cmdline_connect`).


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
see :ref:`cmdline_job_options`; can also be specified via ``$HOD_CREATE_JOB_*``.


.. _cmdline_batch:

``hod batch --script=<script-name>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a cluster and run the script. Upon completion of the script, the cluster will be stopped.

Next to ``--script`` (which is mandatory with ``batch``), all configuration options supported for ``create`` are
also supported for ``batch``, see :ref:`cmdline_create_options`.
When used with ``batch``, these options can also be specified via ``$HOD_BATCH_*``.

Jobs that have completed will remain in the output of ``hod list`` with a job id of ``<no-job>`` until ``hod clean`` 
is run (see :ref:`cmdline_clean`).

.. note:: ``--hod-module``, ``--workdir``, and either ``--hodconf`` or ``--dist`` must be specified.


.. _cmdline_list:

``hod list``
~~~~~~~~~~~~

.. TODO enhance output?

Print a list of existing clusters, and their state ('``queued``' or '``running``').

Jobs that have completed running will remain in the list with ``<no-job>`` until
``hod clean`` is run.

See :ref:`cmdline_clean`.


.. _cmdline_dists:

``hod dists``
~~~~~~~~~~~~~

Print a list of available cluster configuration files.


.. _cmdline_helptemplate:

``hod help-template``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. FIXME machine?

Print the values for the configuration templates based on the current machine.


.. _cmdline_genconfig:

``hod genconfig``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate hanythingondemand cluster configuration files to the working directory for diagnostic purposes.

The working directory can be specified using ``--workdir`` or via ``$HOD_GENCONFIG_WORKDIR``.


.. _cmdline_connect:

``hod connect <cluster label>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. ssh + set up environment (screen no longer needed!)

Connect to an existing hanythingondemand cluster, and set up the environment to use it.

This basically corresponds to logging in to the cluster head node using SSH and sourcing the cluster information script
that was created for this cluster (``$HOME/.config/hod.d/<label>/env``).

.. _cmdline_clean:

``hod clean``
~~~~~~~~~~~~~

Remove cluster info directory for clusters that are no longer available, i.e.  those marked with ``<no-job>`` in the 
output of ``hod list``.
