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
@author: Stijn De Weirdt (Ghent University)
"""

from vsc.utils.generaloption import GeneralOption

class HodOption(GeneralOption):
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
        opts = {'config': ("Top level configuration file. This can be "
                           "a comma separated list of config files with the later files taking "
                           "precendence.", "string", "store", ''),
                'dist': ("Prepackaged Hadoop distribution (e.g.  Hadoop/2.5.0-cdh5.3.1-native). "
                         "This cannot be set if config is set", "string", "store", ''),
                'workdir': ("""Working directory""", "string", "store", None),
                'modules': ("""Extra modules to load in each service environment""", "string", "store", None),
                }
        descr = ["Config", "Configuration files options"]

        self.log.debug("Add config option parser descr %s opts %s", descr, opts)
        self.add_group_parser(opts, descr)

    def make_init(self):
        """Trigger all inits"""
        self.rm_options()
        self.config_options()
