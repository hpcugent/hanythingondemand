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

.. _cmdline_hod_options:

Configuration options for ``hod``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. _cmdline_hod_help:

``hod [subcommand] --help``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Print usage information and supported subcommands along with a short help message for each of them, or usage information
and available options for the specified subcommand.

``hod --hodconf <path>``
^^^^^^^^^^^^^^^^^^^^^^^^

Specify location of cluster configuration file.

``hod --dist <dist label>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``hod --workdir <path>``
^^^^^^^^^^^^^^^^^^^^^^^^


.. _cmdline_hod_version:

``hod --version``
^^^^^^^^^^^^^^^^^

Print hanythingondemand version information.

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
Some of these require to be in a particular state (e.g., being connected to a hanythingondemand cluster).

An overview of the available subcommands is available via :ref:`cmdline_hod_usage`.

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

``hod create [cluster label]``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. TODO label part

Create a hanythingondemand cluster, with the specified label and cluster configuration file.

.. TODO the number part

The configuration file can be a filepath, or a number (that corresponds to a file listed by ``hod dists``).

.. note:: Either the ``--hodconf`` or ``--dist`` option must be specified.

.. _cmdline_create_options:

Configuration options for ``hod create``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _cmdline_create_options_modules:

``hod create --modules <module names>``
+++++++++++++++++++++++++++++++++++++++

Add modules to the dist so each node has access to them. If code submitted to
the cluster requires a particular module, it should be added with this option.
For example, if an IPython notebook plans to use Python modules on the worker
kernels (or through Spark) they will need to be added here.

.. _cmdline_create_options_job:

Configuration options for job scheduler passed via ``hod create``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _cmdline_create_options_job_mail:

``hod create --job-mail``/``-m``
++++++++++++++++++++++++++++++++

Send a mail when the cluster has started or finished.

.. _cmdline_batch:

``hod batch --script=<script-name>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a cluster and run the script. Upon completion of the script, the cluster will be stopped.

.. note:: Either the ``--hodconf`` or ``--dist`` option must be specified.

.. _cmdline_list:

``hod list``
~~~~~~~~~~~~

.. TODO enhance output?

Print a list of existing clusters, and their state ('``submitted``' or '``active``').


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


.. _cmdline_connect:

``hod connect <cluster label>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. ssh + set up environment (screen no longer needed!)

Connect to an existing hanythingondemand cluster, and set up the environment to use it.

If no cluster label is specified, a list of existing clusters is printed (via ``hod list-clusters``).

SSH to head node + set up environment (source $HOME/.config/hod.d/<label>.<jobid>/env)
