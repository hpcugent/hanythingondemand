=========================
Logging and Configuration
=========================
The log files will be in the workdir that you have specified, in ``${USER}.${HOSTNAME}.${PID}/log``

One of the advantages of having the log files on a parallel file system is that one no longer needs to use special tools for log aggregation (Flume, Logstash, Logly, etc) since all the logs for all the nodes are in a single directory structure.
