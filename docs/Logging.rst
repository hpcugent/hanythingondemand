==============
Hadoop Logging
==============
By default, the log files for a Hadoop cluster will be in ``$localworkdir/log``. Expanded, this is in the workdir as follows: ``$workdir/${USER}.${HOSTNAME}.${PID}/log``

One of the advantages of having the log files on a parallel file system is that one no longer needs to use special tools for log aggregation (Flume, Logstash, Logly, etc) since all the logs for all the nodes are in a single directory structure.
