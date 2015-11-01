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
