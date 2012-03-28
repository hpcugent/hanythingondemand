"""
Mapred config and options
"""

from hod.config.types import *
from hod.config.hadoopopts import HadoopOpts
from hod.config.hadoopcfg import HadoopCfg

MAPRED_OPTS = {
    'mapred.job.tracker' : [HostnamePort(':9000'), 'The host and port that the MapReduce job tracker runs at.  If "local", then jobs are run in-process as a single map and reduce task.'],
    'mapred.job.tracker.http.address': [HostnamePort(':50030'), 'The job tracker http server address and port the server will listen on. If the port is 0 then the server will start on a free port.'],
    'mapred.local.dir' : [Directories([None]), 'The local directory where MapReduce stores intermediate data files. May be a comma-separated list of kindoflist on different devices in order to spread disk i/o. Directories that do not exist are ignored.'],
    'mapred.map.tasks' : [None, 'As a rule of thumb, use 10x the number of slaves (i.e., number of TaskTrackers).'],
    'mapred.reduce.tasks' : [None, 'As a rule of thumb, use 2x the number of slave processors (i.e., number of TaskTrackers).'],

    'mapred.task.tracker.task-controller':'Fully qualified class name of the task controller class. Currently there are two implementations of task controller in the Hadoop system, DefaultTaskController and LinuxTaskController. Refer to the class names mentioned above to determine the value to set for the class of choice.',
}

MAPRED_MEMORY_OPTS = {
    'mapred.tasktracker.vmem.reserved':'A number, in bytes, that represents an offset. The total VMEM on the machine, minus this offset, is the VMEM node - limit for all tasks, and their descendants, spawned by the TT.',
    'mapred.task.default.maxvmem':'A number, in bytes, that represents the default VMEM task - limit associated with a task. Unless overridden by a jobs setting, this number defines the VMEM task-limit.',
    'mapred.task.limit.maxvmem':'A number, in bytes, that represents the upper VMEM task-limit associated with a task. Users, when specifying a VMEM task-limit for their tasks, should not specify a limit which exceeds this amount.',
    'mapred.tasktracker.taskmemorymanager.monitoring-interval':'The time interval, in milliseconds, between which the TT checks for any memory violation. The default value is 5000 msec (5 seconds).',
    'mapred.tasktracker.pmem.reserved':'A number, in bytes, that represents an offset. The total physical memory (RAM) on the machine, minus this offset, is the recommended RAM node-limit. The RAM node-limit is a hint to a Scheduler to scheduler only so many tasks such that the sum total of their RAM requirements does not exceed this limit. RAM usage is not monitored by a TT.',
}


## mapred taskset.cfg opts for LinuxTaskController 
## not for xml
#MAPRED_TASKSETCFG_OPTS = {
#    'mapred.local.dir':'Path to mapred local kindoflist. Should be same as the value which was provided to key in mapred-site.xml. This is required to validate paths passed to the setuid executable in order to prevent arbitrary paths being passed to it.',
#    'hadoop.log.dir':'Path to hadoop log directory. Should be same as the value which the TaskTracker is started with. This is required to set proper permissions on the log files so that they can be written to by the users tasks and read by the TaskTracker for serving on the web UI.',
#    'mapreduce.tasktracker.group':'Group to which the TaskTracker belongs. The group owner of the taskcontroller binary should be this group. Should be same as the value with which the TaskTracker is configured. This configuration is required for validating the secure access of the task-controller binary.',
#}


MAPRED_ENV_OPTS = {
    'HADOOP_JOBTRACKER_OPTS':[Arguments(), ''],
    'HADOOP_TASKTRACKER_OPTS':[Arguments(), ''],
}

class MapredCfg(HadoopCfg):
    """Mapred MR1 cfg"""
    def __init__(self):
        HadoopCfg.__init__(self)
        self.name = 'mapred'  ## MR1

class MapredOpts(MapredCfg, HadoopOpts):
    """Mapred options"""
    def __init__(self):
        HadoopOpts.__init__(self)
        MapredCfg.__init__(self)

    def init_defaults(self):
        """Create the default list of params and description"""
        self.log.debug("Adding init defaults.")
        self.add_from_opts_dict(MAPRED_OPTS)

    def set_service_defaults(self, mis):
        """Set service specific default"""
        self.log.debug("Setting servicedefaults for %s" % mis)

