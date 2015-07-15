#!/usr/bin/env python
# #
# Copyright 2009-2015 Ghent University
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
Generate a PBS job script using pbs_python. Will use mympirun to get the all started

@author: Stijn De Weirdt (Universiteit Gent)
@author: Ewan Higgs (Universiteit Gent)
"""

from hod.applications.application import Application
from hod.rmscheduler.hodjob import PbsHodJob
from vsc.utils.generaloption import GeneralOption
from textwrap import dedent

from vsc.utils import fancylogger
_log = fancylogger.getLogger(fname=False)

class CreatePbsApplication(Application):
    def usage(self):
        s ="""\
        hod pbs - Submit a job to spawn a cluster on a PBS job controller.
        hod pbs --config-config=<hod.conf file> --config-workdir=<working directory>
        """
        return dedent(s)

    def run(self, args):
        try:
            options = CreatePbsOption(go_args=args)
            j = PbsHodJob(options)
            j.run()
        except StandardError, e:
            fancylogger.setLogFormat(fancylogger.TEST_LOGGING_FORMAT)
            fancylogger.logToScreen(enable=True)
            _log.raiseException(e.message)


class CreatePbsOption(GeneralOption):
    '''
    Command line options for hod_pbs.
    '''
    def rm_options(self):
        """Make the rm related options"""
        opts = {"walltime": ("Job walltime in hours", 'float', 'store', 48, 'l'),
                "nodes": ("Full nodes for the job", "int", "store", 5, "n"),
                "ppn": ("Processors per node (-1=full node)", "int", "store", -1),
                "mail": ("When to send mail (b=begin, e=end, a=abort)", "string", "extend", [], "m"),
                "mailothers": ("Other email adresses to send mail to", "string", "extend", [], "M"),
                "name": ("Job name", "string", "store", "HanythingOnDemand_job", "N"),
                "queue": ("Queue name (empty string is default queue)", "string", "store", "", "q"),
                }
        descr = ["Resource manager / Scheduler", "Provide resource manager/scheduler related options (eg number of nodes)"]

        prefix = 'rm'
        self.log.debug("Add resourcemanager option parser prefix %s descr %s opts %s", 
                prefix, descr, opts)
        self.add_group_parser(opts, descr, prefix=prefix)

    def config_options(self):
        """Make the action related options"""
        opts = {'config': ("""Top level configuration file. This can be
a comma separated list of config files with the later files taking
precendence.""", "string", "store", ''),
                'workdir': ("""Working directory""", "string", "store", None),
                'modules': ("""Extra modules to load in each service environment""", "string", "store", None),
                }
        descr = ["Config", "Configuration files options"]

        prefix = 'config'
        self.log.debug("Add config option parser prefix %s descr %s opts %s",
                prefix, descr, opts)
        self.add_group_parser(opts, descr, prefix=prefix)

    def mympirun_options(self):
        """Some mympiprun options"""
        opts = {'debug': ("Run mympirun in debug mode", None, "store_true", False)}
        descr = ['mympirun', 'Provide mympirun related options']
        prefix = 'mympirun'

        self.log.debug("Add mympirun option parser prefix %s descr %s opts %s",
                prefix, descr, opts)
        self.add_group_parser(opts, descr, prefix=prefix)


    def make_init(self):
        """Trigger all inits"""
        self.rm_options()
        self.config_options()
        self.mympirun_options()
