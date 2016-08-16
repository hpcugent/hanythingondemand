# 3.1.2
* also take --modulepaths into account for HOD jobs (not just for interactive sessions)

# 3.1.1
* add support for --modulepaths to specify the location of custom modules

# 3.1.0
* add dist with IPython 4.2.0
* add Travis configuration

# 3.0.4
* IPython 3.2.3 with Spark 1.6 is now bundled as an available distribution.
* Faster startup time on multiple nodes.
* Fix a bug for multinode Spark clusters where the localworkdir was shared.

# 3.0.3
* Autogenerate Yarn vcore settings. Otherwise the hard coded default of '8' is
  chosen, which is not ideal.

# 3.0.2
* Fix for `hod batch` so it has the same environment as a shell started with
  `hod connect`. This is required to use YARN instead of Hadoop LocalJobRunner.
* Enhancements to IPython/Spark so Spark starts up with more executors, memory,
  and cores than the paltry defaults.

# 3.0.1
* Fix for multi node configurations where `PBS_` environment variables were not
  being passed to MPI slave environments. This prevented multi node
  configurations from working correctly because they use `$PBS_JOBID` in finding
  the localworkdir..
* Minor fix to error reporting in `hod clean`.

# 3.0.0
* [Command line reorganization](http://hod.readthedocs.org/en/latest/Command_line_interface.html). 
  `hod` now uses a command/subcommand style interface which reduces the number of possible conflicting flags.
* `hod batch` mode so users can start a cluster, run a job, and quit.
* `hod connect` so users can connect and reconnect without the risk of
  losing their screen session.
* Job labels. Used in conjunction with `hod connect`. Users can also relabel
  their jobs using `hod relabel`
* Support for IPython notebooks with Spark as a back end.
* Support for HBase.
* [Extensive
* documentation](http://hod.readthedocs.org/en/latest/Connecting_to_web_UIs.html) 
  covering Windows, OS X, and Linux for using `hod` web services.
* Internal improvements that might not be visible to users:
  * Support for zipped eggs. This speeds up the command line experience when
    running `hod` from a shared file system since there are less files to poke
    through.
  * Support for Python 2.6.
  * Using Jenkins for continuous integration for improved quality.
  * Improved test coverage for improved quality.
