# #
# Copyright 2009-2013 Ghent University
#
# This file is part of hanythingondemand
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/hanythingondemand
#
# hanythingondemand is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# hanythingondemand is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hanythingondemand. If not, see <http://www.gnu.org/licenses/>.
# #
"""
Mapred config and options

@author: Stijn De Weirdt
"""

from hod.config.customtypes import HostnamePort, Directories, Arguments, ParamsDescr, UserGroup, Params, Boolean
from hod.config.hadoopopts import HadoopOpts, Option
from hod.config.hadoopcfg import HadoopCfg
import re

MAPRED_OPTS = ParamsDescr({
    'mapred.job.tracker': Option(HostnamePort, ':9000', 'The host and port that the MapReduce job tracker runs at.  If "local", then jobs are run in-process as a single map and reduce task.'),
    'mapred.local.dir': Option(Directories, None, 'The local directory where MapReduce stores intermediate data files. May be a comma-separated list of kindoflist on different devices in order to spread disk i/o. Directories that do not exist are ignored.'),
    'mapred.map.tasks': Option(str, None, 'As a rule of thumb, use 10x the number of slaves (i.e., number of TaskTrackers).'),
    'mapred.reduce.tasks': Option(str, None, 'As a rule of thumb, use 2x the number of slave processors (i.e., number of TaskTrackers).'),

    'mapred.tasktracker.map.tasks.maximum': Option(str, None, 'The maximum number of map tasks (default is 2)'),
    'mapred.tasktracker.reduce.tasks.maximum': Option(str, None, 'The maximum number of map tasks (default is 2)'),


     'mapred.child.java.opts' : Option(Arguments, '-Xmx1024M', 'General java options passed to each task JVM'), 

    'mapred.job.reuse.jvm.num.tasks': Option(str, '2', 'Reuse the JVM between tasks If the value is 1 (the default), then JVMs are not reused (i.e. 1 task per JVM) (-1: no limit)'),  # from myhadoop

    'mapred.task.tracker.task-controller': Option(str, '', '''Fully qualified
    class name of the task controller class. Currently there are two
    implementations of task controller in the Hadoop system,
    DefaultTaskController and LinuxTaskController. Refer to the class names
    mentioned above to determine the value to set for the class of choice.'''),
    'mapred.map.tasks.speculative.exectution': Option(Boolean, True, 'If true, then multiple instances of some map tasks may be executed in parallel.'),
    'mapred.reduce.tasks.speculative.exectution': Option(Boolean, True, 'If true, then multiple instances of some reduce tasks may be executed in parallel.'),
    'mapred.reduce.parallel.copies': Option(int, 5, 'The default number of parallel transfers run by reduce during the copy(shuffle) phase.'),
    'mapred.compress.map.output': Option(str, '', ''),
})

MAPRED_SECURITY_SERVICE = ParamsDescr({
    'security.inter.tracker.protocol.acl': Option(UserGroup, None, 'ACL for InterTrackerProtocol, used by the tasktrackers to communicate with the jobtracker.'),
    'security.job.submission.protocol.acl': Option(UserGroup, None, 'ACL for JobSubmissionProtocol, used by job clients to communciate with the jobtracker for job submission, querying job status etc.'),
    'security.task.umbilical.protocol.acl': Option(UserGroup, None, 'ACL for TaskUmbilicalProtocol, used by the map and reduce tasks to communicate with the parent tasktracker.'),
})


MAPRED_MEMORY_OPTS = ParamsDescr({
    'mapred.tasktracker.vmem.reserved': Option(str, None, '''A number, in bytes, that
    represents an offset. The total VMEM on the machine, minus this offset, is
    the VMEM node - limit for all tasks, and their descendants, spawned by the
    TT.'''),
    'mapred.task.default.maxvmem': Option(str, None, '''A number, in bytes, that
    represents the default VMEM task - limit associated with a task. Unless
    overridden by a jobs setting, this number defines the VMEM task-limit.'''),
    'mapred.task.limit.maxvmem': Option(str, None, '''A number, in bytes, that
    represents the upper VMEM task-limit associated with a task. Users, when
    specifying a VMEM task-limit for their tasks, should not specify a limit
    which exceeds this amount.'''),
    'mapred.tasktracker.taskmemorymanager.monitoring-interval': Option(str, None,
    '''The time interval, in milliseconds, between which the TT checks for any
    memory violation. The default value is 5000 msec (5 seconds).'''),
    'mapred.tasktracker.pmem.reserved': Option(str, None, '''A number, in bytes, that
    represents an offset. The total physical memory (RAM) on the machine, minus
    this offset, is the recommended RAM node-limit. The RAM node-limit is a hint
    to a Scheduler to scheduler only so many tasks such that the sum total of
    their RAM requirements does not exceed this limit. RAM usage is not
    monitored by a TT.'''),
})

MAPRED_HTTP_OPTS = ParamsDescr({
    'mapred.job.tracker.http.address': Option(HostnamePort, ':50030', 'The job tracker http server address and port the server will listen on. If the port is 0 then the server will start on a free port.'),
})

# # mapred taskset.cfg opts for LinuxTaskController
# # not for xml
# MAPRED_TASKSETCFG_OPTS = {
#    'mapred.local.dir': [str, None, 'Path to mapred local kindoflist. Should be
#    same as the value which was provided to key in mapred-site.xml. This is
#    required to validate paths passed to the setuid executable in order to
#    prevent arbitrary paths being passed to it.'],
#    'hadoop.log.dir': [str, None, 'Path to hadoop log directory. Should be same
#    as the value which the TaskTracker is started with. This is required to set
#    proper permissions on the log files so that they can be written to by the
#    users tasks and read by the TaskTracker for serving on the web UI.'],
#    'mapreduce.tasktracker.group': [str, None, 'Group to which the TaskTracker
#    belongs. The group owner of the taskcontroller binary should be this group.
#    Should be same as the value with which the TaskTracker is configured. This
#    configuration is required for validating the secure access of the
#    task-controller binary.'],
# }


MAPRED_ENV_OPTS = ParamsDescr({
    'HADOOP_JOBTRACKER_OPTS': Option(Arguments, None, ''),
    'HADOOP_TASKTRACKER_OPTS': Option(Arguments, None, ''),
})


class MapredOpts(HadoopOpts):
    """Mapred options"""
    def __init__(self, shared=None, basedir=None):
        HadoopOpts.__init__(self, shared=shared, basedir=basedir)
        self.name = 'mapred'  # MR1

    def init_defaults(self):
        """Create the default list of params and description"""
        self.log.debug("Adding init defaults.")
        self.add_from_opts_dict(MAPRED_OPTS)

    def init_security_defaults(self):
        """Add security options"""
        self.log.debug("Add mapred security settings")
        self.add_from_opts_dict(MAPRED_SECURITY_SERVICE)

    def init_core_defaults_shared(self, shared):
        """Add hbase code"""
        self.check_hbase()

        self.log.debug("Adding init shared core params")
        self.add_from_opts_dict(shared.get('params', ParamsDescr({})))

        self.log.debug("Adding init shared core env_params")
        self.add_from_opts_dict(
            shared.get('env_params', ParamsDescr({})), update_env=True)

    def check_hbase(self):
        """hbase support
            - we need the HBase config files (or config info)
            - add hbase jars + conf +zookeeper to HADOOP_CLASSPATH eg
            $HBASE_HOME/build/hbase-X.X.X.jar:$HBASE_HOME/build/hbase-X.X.X-test.jar:$HBASE_HOME/conf:${HBASE_HOME}/lib/zookeeper-X.X.X.jar
        """
        # # TODO now we are going to assume that the regionservers are also the tasktrackers, so the config files are available

        # # locate the HBase work

        # # Code basedon Client config init_core_defaults_shared
        exclude_params = [r'\.dir$',
                          r'^mapred.local',
                          ]
        exclude_env_params = [r'_DIR$']

        # # make compiled regexp
        exclude_params = [re.compile(x) for x in exclude_params]
        exclude_env_params = [re.compile(x) for x in exclude_env_params]

        # # first parse the params from the (previously initiated) active work
        # # - they are updated in the order they are started (last)
        prev_params = ParamsDescr()
        prev_env_params = ParamsDescr()

        found_hbase = False
        for act_work in self.shared_opts['active_work']:
            name = act_work['work_name']
            params = act_work.get('params', Params({}))
            env_params = act_work.get('env_params', Params({}))
            if name == 'Hbase':
                self.log.debug("Active work from %s params %s env_params %s" %
                               (name, params, env_params))

                for k, v in params.items():
                    for excl_k in exclude_params:
                        if not excl_k.search(k):
                            prev_params.update({k: [v, '']})
                            continue

                for k, v in env_params.items():
                    for excl_k in exclude_env_params:
                        if not excl_k.search(k):
                            prev_env_params.update({k: [v, '']})
                            continue

                jars = ":".join(act_work['hbase_jars'])
                jar_env_params = ParamsDescr(
                    {'HADOOP_CLASSPATH': [jars, 'Added HBase jars']})

                found_hbase = True
                break
            else:
                self.log.debug(
                    "Looking for HBase work, ignoring %s work" % name)

        if found_hbase:
            self.log.debug("Hbase found, adding some of the params")
            self.add_from_opts_dict(prev_params)
            self.add_from_opts_dict(prev_env_params, update_env=True)

            self.log.debug("Added jar env params %s" % jar_env_params)
            self.add_from_opts_dict(jar_env_params, update_env=True)
        else:
            self.log.debug('Hbase not found, no params added')
