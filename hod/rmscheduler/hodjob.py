# #
# Copyright 2009-2016 Ghent University
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

import hod
from hod.rmscheduler.job import Job
from hod.rmscheduler.rm_pbs import Pbs
from hod.rmscheduler.resourcemanagerscheduler import ResourceManagerScheduler
from hod.config.config import (parse_comma_delim_list,
        PreServiceConfigOpts, resolve_config_paths)


class HodJob(Job):
    """Hanything on demand job"""

    OPTION_IGNORE_PREFIX = ['job', 'action']

    def __init__(self, options):
        super(HodJob, self).__init__(options)

        # TODO abs path?
        self.pythonexe = 'python'
        self.hodargs = self.options.generate_cmd_line(ignore='^(%s)_' % '|'.join(self.OPTION_IGNORE_PREFIX))

        self.hodenvvarprefix = ['HOD', 'PBS']

        self.set_type_class()

        # HOD_<label> if label is given; HOD_job otherwise.
        self.name_prefix = 'HOD'
        options_dict = self.options.dict_by_prefix()
        label = self.options.options.label
        if label is None:
            label = 'job'
        options_dict['job']['name'] = "%s_%s" % (self.name_prefix, label)

        self.type = self.type_class(options_dict['job'])

        # all jobqueries are filtered on this suffix
        self.type.job_filter = {'Job_Name': '^%s' % self.name_prefix}

        self.run_in_cwd = True

        self.main_out = "$%s/hod.output.$%s" % (self.type.vars['cwd'], self.type.vars['jobid'])

    def set_type_class(self):
        """Set the typeclass"""
        self.log.debug("Using default class ResourceManagerScheduler.")
        self.type_class = ResourceManagerScheduler

    def run(self):
        """Do stuff based upon options"""
        self.submit()

    def state(self):
        """Find the job information of submitted jobs"""
        return self.type.state()

class MympirunHod(HodJob):
    """Hod type job using mympirun cmd style."""
    OPTION_IGNORE_PREFIX = ['job', 'action', 'mympirun']

    def generate_exe(self):
        """Mympirun executable"""

        main = ['mympirun']

        if self.options.options.debug:
            main.append('--debug')

        if self.main_out:
            main.append('--output=%s' % self.main_out)

        # single MPI process per node
        main.append("--hybrid=1")

        main.append('--variablesprefix=%s' % ','.join(self.hodenvvarprefix))

        main.append("%s -m hod.local" % self.pythonexe)

        main.extend(self.hodargs)

        self.log.debug("Generated main command: %s", main)
        return [' '.join(main)]


class PbsHodJob(MympirunHod):
    """PbsHodJob type job for easybuild infrastructure
        - easybuild module names
    """
    def __init__(self, options):
        super(PbsHodJob, self).__init__(options)

        self.modules = [options.options.hod_module]

        config_filenames = resolve_config_paths(options.options.hodconf, options.options.dist)
        self.log.debug('Manifest config paths resolved to: %s', config_filenames)
        config_filenames = parse_comma_delim_list(config_filenames)
        self.log.info('Loading "%s" manifest config', config_filenames)
        # If the user mistypes the --dist argument (e.g. Haddoop-...) then this will
        # raise; TODO: cleanup the error reporting. 
        precfg = PreServiceConfigOpts.from_file_list(config_filenames, workdir=options.options.workdir,
                                                     modulepaths=options.options.modulepaths,
                                                     modules=options.options.modules)
        for modulepath in precfg.modulepaths:
            self.log.debug("Adding extra module path '%s' to startup script", modulepath)
            self.modulepaths.append(modulepath)
        for module in precfg.modules:
            self.log.debug("Adding '%s' module to startup script.", module)
            self.modules.append(module)

    def set_type_class(self):
        """Set the typeclass"""
        self.log.debug("Using default class Pbs.")
        self.type_class = Pbs
