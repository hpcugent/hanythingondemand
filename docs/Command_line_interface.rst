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
    hod: hanythingondemand - Run services within a torque cluster
    usage: hod [--version] [--help] <subcommand> [subcommand options]
    Available subcommands:
        create          Submit a job to spawn a cluster on a PBS job controller
        list            List submitted/running clusters
        dists           List the available distributions
        help-template   Print the values of the configuration templates based on the current machine.
        genconfig       Write hod configs to a directory for diagnostic purposes


.. _cmdline_hod_options:

Configuration options for ``hod``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. _cmdline_hod_help:

``hod --help``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Print usage information and supported subcommand, along with a short help message for each of them.

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


.. _cmdline_hod_subcommands:

``hod`` subcommands
-------------------

The ``hod`` command provides a number of subcommands, which correspond to different actions.
Some of these require to be in a particular state (e.g., being connected to a hanythingondemand cluster).

An overview of the available subcommands is available via :ref:`cmdline_hod_usage`.

More details on a specific subcommand are available via ``hod <subcommand> --help``.

Known subcommands:

* :ref:`cmdline_create`
* :ref:`cmdline_list`
* :ref:`cmdline_dists`
* :ref:`cmdline_helptemplate`
* :ref:`cmdline_genconfig`
* :ref:`cmdline_connect`
* :ref:`cmdline_destroy`
* :ref:`cmdline_disconnect`
* :ref:`cmdline_status`

.. _cmdline_hod_subcommands_options:

Generic configuration options for subcommands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _cmdline_hod_subcommands_options_help:

``hod <subcommand> --help``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. -----------
.. SUBCOMMANDS
.. -----------

.. _cmdline_create:

.. TODO label part

``hod create [cluster label]``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

foo

.. _cmdline_create_options_job:

Configuration options for job scheduler passed via ``hod create``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

foo

.. _cmdline_create_options_job_mail:

``hod create --job-mail``/``-m``
++++++++++++++++++++++++++++++++

foo

.. _cmdline_list:

.. TODO enhance output?

``hod list``
~~~~~~~~~~~~

Print a list of existing clusters, and their state ('``submitted``' or '``active``').


.. _cmdline_dists:

``hod dists``
~~~~~~~~~~~~~

Print a numbered list of available cluster configuration files.


.. _cmdline_helptemplate:

``hod help-template`` (rename??)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. FIXME machine?

Print the values for the configuration templates based on the current machine.


.. _cmdline_genconfig:

``hod genconfig`` (rename??)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate hanythingondemand cluster configuration files to the working directory for diagnostic purposes.



.. TODO
.. _cmdline_connect:

``hod connect <cluster label>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. ssh + set up environment (screen no longer needed!)

Connect to an existing hanythingondemand cluster, and set up the environment to use it.

If no cluster label is specified, a list of existing clusters is printed (via ``hod list-clusters``).

SSH to head node + set up environment (source $HOME/.config/hod.d/<label>.<jobid>/env)

.. TODO
.. _cmdline_destroy:

``hod destroy <cluster label>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. qdel

Destroy an existing hanythingondemand cluster.

If no cluster label is specified, a list of existing clusters is printed (via ``hod list-clusters``).


.. TODO
.. _cmdline_disconnect:

``hod disconnect``
~~~~~~~~~~~~~~~~~~

.. exit SSH session

Disconnect from the cluster ``hod`` is currently connected to (if any).


.. TODO
.. _cmdline_status:

``hod status <cluster label>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Print current status, i.e. whether we are connected to a cluster (and if so, which one), etc.

If a cluster label is specified, a more detailed status of the specific cluster is printed.
