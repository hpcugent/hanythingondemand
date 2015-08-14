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

@author: Stijn De Weirdt (University of Ghent)
"""

import os
import sys

from hod.rmscheduler.job import Job
from hod.rmscheduler.resourcemanagerscheduler import ResourceManagerScheduler
from hod.config.config import (parse_comma_delim_list,
        preserviceconfigopts_from_file_list, resolve_config_paths)


class HodJob(Job):
    """Hanything on demand job"""

    OPTION_IGNORE_PREFIX = ['job', 'action']

    def __init__(self, options):
        super(HodJob, self).__init__(options)

        self.exeout = None

        # TODO abs path?
        self.pythonexe = 'python'
        self.hodexe, self.hodpythonpath = self.get_hod()
        self.hodargs = self.options.generate_cmd_line(ignore='^(%s)_' % '|'.join(self.OPTION_IGNORE_PREFIX))

        self.hodenvvarprefix = ['HOD']

        self.set_type_class()

        self.name_suffix = 'HOD'  # suffixed name, to lookup later
        options_dict = self.options.dict_by_prefix()
        options_dict['job']['name'] = "%s_%s" % (options_dict['job']['name'],
                                                self.name_suffix)
        self.type = self.type_class(options_dict['job'])

        # all jobqueries are filtered on this suffix
        self.type.job_filter = {'Job_Name': '%s$' % self.name_suffix}

        self.run_in_cwd = True

        self.exeout = "$%s/hod.output.$%s" % (
            self.type.vars['cwd'], self.type.vars['jobid'])

    def set_type_class(self):
        """Set the typeclass"""
        self.log.debug("Using default class ResourceManagerScheduler.")
        self.type_class = ResourceManagerScheduler

    def get_hod(self, exe_name='hod-local'):
        """Get the full path of the exe_name
             -look in bin or bin / .. / hod /
        """
        fullscriptname = os.path.abspath(sys.argv[0])

        bindir = os.path.dirname(fullscriptname)
        hodpythondir = os.path.abspath("%s/.." % bindir)
        hoddir = os.path.abspath("%s/../hod" % bindir)

        self.log.debug("Found fullscriptname %s binname %s hoddir %s",
                       fullscriptname, bindir, hoddir)

        fn = None
        paths = [bindir, hoddir]
        for tmpdir in paths:
            fn = os.path.join(tmpdir, exe_name)
            if os.path.isfile(fn):
                self.log.debug("Found exe_name %s location %s", exe_name, fn)
                break
            else:
                fn = None
        if not fn:
            self.log.error("No exe_name %s found in paths %s", exe_name, paths)

        return fn, hodpythondir

    def run(self):
        """Do stuff based upon options"""
        self.submit()
        msg = self.type.state()
        print msg


class MympirunHod(HodJob):
    """Hod type job using mympirun cmd style."""
    OPTION_IGNORE_PREFIX = ['job', 'action', 'mympirun']

    def generate_exe(self):
        """Mympirun executable"""

        exe = ["mympirun"]
        if self.options.options.debug:
            exe.append("--debug")
        if self.exeout:
            exe.append("--output=%s" % self.exeout)
        exe.append("--hybrid=1")

        exe.append('--variablesprefix=%s' % ','.join(self.hodenvvarprefix))

        exe.append(self.pythonexe)
        exe.append(self.hodexe)

        exe.extend(self.hodargs)

        self.log.debug("Generated exe %s", exe)
        return [" ".join(exe)]


class PbsHodJob(MympirunHod):
    """PbsHodJob type job for easybuild infrastructure
        - easybuild module names
    """
    def __init__(self, options):
        super(PbsHodJob, self).__init__(options)
        self.modules = []

        modname = 'hanythingondemand'
        # TODO this is undefined, module should be provided via E, eg EBMODULENAME
        ebmodname_envvar = 'EBMODNAME%s' % modname.upper()

        ebmodname = os.environ.get(ebmodname_envvar, None)
        if ebmodname is None:
            # TODO: is this environment modules specific?
            env_list = 'LOADEDMODULES'
            self.log.debug('Missing environment variable %s, going to guess it via %s and modname %s.',
                    ebmodname_envvar, env_list, modname)
            candidates = [x for x in os.environ.get(env_list, '').split(':') if x.startswith(modname)]
            if candidates:
                ebmodname = candidates[-1]
                self.log.debug("Using guessed modulename %s", ebmodname)
            else:
                self.log.raiseException('Failed to guess modulename and no EB environment variable %s set.' %
                        ebmodname_envvar)

        # FIXME
        self.modules.append(ebmodname)

        config_filenames = resolve_config_paths(options.options.hodconf, options.options.dist)
        self.log.debug('Manifest config paths resolved to: %s', config_filenames)
        config_filenames = parse_comma_delim_list(config_filenames)
        self.log.info('Loading "%s" manifest config', config_filenames)
        # If the user mistypes the --dist argument (e.g. Haddoop-...) then this will
        # raise; TODO: cleanup the error reporting. 
        precfg = preserviceconfigopts_from_file_list(config_filenames, workdir=options.options.workdir)
        for module in precfg.modules:
            self.log.debug("Adding '%s' module to startup script.", module)
            self.modules.append(module)

    def set_type_class(self):
        """Set the typeclass"""
        self.log.debug("Using default class Pbs.")
        from hod.rmscheduler.rm_pbs import Pbs
        self.type_class = Pbs
