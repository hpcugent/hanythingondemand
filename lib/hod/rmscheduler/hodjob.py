##
# Copyright 2009-2012 Ghent University
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
##
"""

@author: Stijn De Weirdt
"""

import os
import sys

from hod.rmscheduler.job import Job
from hod.rmscheduler.resourcemanagerscheduler import ResourceManagerScheduler


class HodJob(Job):
    """Hanything on demand job"""
    def __init__(self, options=None):
        if options is None:
            from hod.config.hodoption import HodOption
            options = HodOption()

        Job.__init__(self, options)

        self.exeout = None

        self.hodexe, self.hodpythonpath = self.get_hod()
        self.hodargs = self.options.generate_cmd_line(ignore='^(rm|action)_')

        self.hodenvvarprefix = ['HADOOP', 'JAVA', 'HOD', 'MAPRED', 'HDFS']
        if not self.options.options.hdfs_off:
            self.hodenvvarprefix.append('HDFS')
        if not self.options.options.mr1_off:
            self.hodenvvarprefix.append('MAPRED')
        if self.options.options.yarn_on:
            self.hodenvvarprefix.append('YARN')
        if self.options.options.hbase_on:
            self.hodenvvarprefix.append('HBASE')

        self.set_type_class()

        self.name_suffix = 'HOD'  # suffixed name, to lookup later
        options_dict = self.options.dict_by_prefix()
        options_dict['rm']['name'] = "%s_%s" % (options_dict['rm'][
                                                'name'], self.name_suffix)
        self.type = self.type_class(options_dict['rm'])

        self.type.job_filter = {'Job_Name': '%s$' %
                                self.name_suffix}  # all jobqueries are filter on this suffix

        self.run_in_cwd = True

        self.exeout = "$%s/hod.output.$%s" % (
            self.type.vars['cwd'], self.type.vars['jobid'])

    def set_type_class(self):
        """Set the typeclass"""
        self.log.debug("Using default class ResourceManagerScheduler.")
        self.type_class = ResourceManagerScheduler

    def get_hod(self, exe_name='hod_main.py'):
        """Get the full path of the exe_name
 -look in bin or bin / .. / hod /
        """
        fullscriptname = os.path.abspath(sys.argv[0])

        bindir = os.path.dirname(fullscriptname)
        hodpythondir = os.path.abspath("%s/.." % bindir)
        hoddir = os.path.abspath("%s/../hod" % bindir)

        self.log.debug("Found fullscriptname %s binname %s hoddir %s" %
                       (fullscriptname, bindir, hoddir))

        fn = None
        paths = [bindir, hoddir]
        for tmpdir in paths:
            fn = os.path.join(tmpdir, exe_name)
            if os.path.isfile(fn):
                self.log.debug(
                    "Found exe_name %s location %s" % (exe_name, fn))
                break
            else:
                fn = None
        if not fn:
            self.log.error(
                "No exe_name %s found in paths %s" % (exe_name, paths))

        return fn, hodpythondir

    def run(self):
        """Do stuff based upon options"""
        options_dict = self.options.dict_by_prefix()
        actions = options_dict['action']
        self.log.debug("Found actions %s" % actions)
        if actions.get('create', False):
            self.submit()
            msg = self.type.state()
            print msg
        elif actions.get('remove', None):
            self.type.remove()
        elif actions.get('show', None):
            msg = self.type.state()
            print msg
        elif actions.get('showall', False):  # should be True
            msg = self.type.state()
            print msg
        else:
            self.log.error("Unknown action in actions %s" % actions)


class EasybuildPbsHod(HodJob):
    """Hod type job for easybuild infrastructure
        - type PBS
        - mympirun cmd style
 -easybuild module names
    """
    def __init__(self, options=None):
        HodJob.__init__(self, options)

        self.modules = ['scripts', 'Python']  # no version?

        self.modules.append('Hadoop/%s' % self.options.options.hadoop_module)

        if self.options.options.hbase_on:
            self.modules.append('HBase/%s' % self.options.options.hbase_module)

        if self.options.options.java_module:
            ## force Java module
            self.modules.append(['unload', 'Java'])
            self.modules.append('Java/%s' % self.options.options.java_module)
                                ## TODO fixed version of 170_3

    def set_type_class(self):
        """Set the typeclass"""
        self.log.debug("Using default class Pbs.")
        from hod.rmscheduler.rm_pbs import Pbs
        self.type_class = Pbs

    def generate_extra_environment(self):
        """load the HOD module, this will set all the environments correctly"""
        version = os.env.get('EBVERSIONHOD', None)
        # if version is not set we don't specify it, but also don't specify the '/'
        if version:
            version = "/%s" % version
        else:
            version = ""
        hodenv = """module load HOD%s\n""" % version

        self.log.debug("Added extra environment %s" % hodenv)

        return [hodenv]

    def generate_exe(self):
        """Mympirun executable"""

        exe = ["mympirun"]
        if self.exeout:
            exe.append("--output=%s" % self.exeout)
        exe.append("--hybrid=1")

        exe.append('--variablesprefix=%s' % ','.join(self.hodenvvarprefix))

        exe.append('python')  # TODO abs path?
        exe.append(self.hodexe)
        exe += self.hodargs

        exe.append("--hod_envclass=%s" % self.__class__.__name__)
                   ## pass the classname so the environment can be re-setup

        self.log.debug("Generated exe %s" % exe)
        return [" ".join(exe)]
