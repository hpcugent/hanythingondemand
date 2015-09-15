.. _logging:

Logging
=======

If your job didn't work as expected, you'll need to check the logs.

It's important to realise that both *hanythingondemand* itself and the services it is running (e.g. Hadoop) produce
logs.

Which logs you should be diving into depends on the information you are looking for or the kind of problems
you run into.

.. contents::
    :depth: 2
    :backlinks: none

.. _logging_hod_logs:

*hanythingondemand* logs
------------------------

For *hanythingondemand* itself, there are three places to consider:

1. When submitting your job to start the cluster, hanythingondemand logs to
   your terminal session. The potential errors here are usually:

   * PBS isn't running or isn't accessible. If so, contact your administrators.

   * Your environment is broken. For example, if you're using a Python version
     for a cluster that doesn't work on the login node.

2. If PBS is accessible and tries to run the job but it failed to start
   properly (e.g. due to a problem with MPI) you will see errors in
   ``Hanythingondemand.e${PBS_JOBID}``. This will be in the directory from
   where you ran the job.

3. When PBS starts your job, it will start logging to
   ``hod.output.$(hostname).$(pid)``. If your service configuration files
   have problems (e.g. typos in the commands, bad paths, etc) then the
   error will be here. For example if a service failed to start you will
   see a message in the logs saying: ``Problem occured with cmd``.

.. _logging_service_logs:

Service logs
------------

.. _logging_service_logs_hadoop:

Hadoop logs
***********

By default, the log files for a Hadoop cluster will be in ``$HOD_LOCALWORKDIR/log``.

One of the advantages of having the log files on a parallel file system is that
one no longer needs to use special tools for log aggregation (Flume, Logstash,
Logly, etc) since all the logs for all the nodes are in a single directory
structure.

Hadoop logs have two components:

1. *Service logs*: These are in ``$HOD_LOCALWORKDIR/log``. Examples are:
   ``yarn-username-resourcemanager-node.domain.out``,
   ``yarn-username-nodemanager-node.domain.out``.

2. *Container logs*: Each piece of Hadoop work takes place in a container.
   Output from your program will appear in these files.  These
   are organized by application/container/stderr and stdout. For example: ::

   $HOD_LOCALWORKDIR/log/userlogs/application_1430748293929_0001/container_1430748293929_0001_01_000003/stdout

IPython logs
************

IPython logs to stdout and stderr. These are sent by hanythingondemand to
``$HOD_LOCALWORKDIR/log/pyspark.stdout`` and ``$HOD_LOCALWORKDIR/log/pyspark.stderr``
