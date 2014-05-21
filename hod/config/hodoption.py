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
@author: Stijn De Weirdt
"""

import os

from vsc.utils.generaloption import GeneralOption


class HodOption(GeneralOption):
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
        self.log.debug("Add resourcemanager option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def action_options(self):
        """Make the action related options"""
        opts = {"create": ("Create and submit new HOD job", None, "store_true", False, 'C'),
                "showall": ("Show info on all found HOD jobs (this is the default action)", None, "store_true", True),
                # "showjob":("Show info for HOD job JOBID", "string", "store", ''),
                # "removejob":("Remove HOD job JOBID", "string", "store", ''),
                }
        descr = ["Action", "What action to take"]

        prefix = 'action'
        self.log.debug("Add action option parser prefix %s descr %s opts %s" %
                       (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def config_options(self):
        """Make the action related options"""
        opts = {'dir': ("Configuration directory", "string", "store", ''),
                }
        descr = ["Config", "Configuration files options"]

        prefix = 'config'
        self.log.debug("Add config option parser prefix %s descr %s opts %s" %
                       (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)


    def hdfs_options(self):
        """Some hdfs presets"""
        opts = {'off': ("Don't start HDFS", None, "store_true", False),
                }
        descr = ['HDFS', 'Provide HDFS related options']
        prefix = 'hdfs'

        self.log.debug("Add HDFS option parser prefix %s descr %s opts %s" %
                       (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def mapred_options(self):
        """Some mapred presets"""
        opts = {'off': ("Don't start MapRed (MR1)", None, "store_true", False),
               }
        descr = ['MapReduce', 'Provide MapReduce (MR1) related options']
        prefix = 'mr1'

        self.log.debug("Add MapRed option parser prefix %s descr %s opts %s" %
                       (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def hadoop_options(self):
        """Some hadoop presets"""
        opts = {'module': ("Use Hadoop module version", "string",
                           "store", os.environ.get("EBVERSIONHADOOP", '')),
               }
        descr = ['Hadoop', 'Provide Hadoop related options']
        prefix = 'hadoop'

        self.log.debug("Add Hadoop option parser prefix %s descr %s opts %s" %
                       (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def hod_options(self):
        """Some HOD presets"""
        opts = {
            'envclass': ("Use HodJob class to create working enviromnet", "string", "store", ""),
            'envscript': ("Use script to create working enviromnet", "string", "store", ""),
            'script': ("Run this script as start of local client screen session", "string", "store", ''),
        }
        descr = ['HOD', 'Provide HOD related options']
        prefix = 'hod'

        self.log.debug("Add Hod option parser prefix %s descr %s opts %s" %
                       (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def hbase_options(self):
        """Some hbase presets"""
        opts = {'on': ("Start HBase", None, "store_true", False),
                'module': ("Use HBase module version", "string", "store", "0.90.4-cdh3u3"),
                }
        descr = ['HBase', 'Provide HBase related options']
        prefix = 'hbase'

        self.log.debug("Add HBase option parser prefix %s descr %s opts %s" %
                       (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def yarn_options(self):
        """Some hbase presets"""
        # Yarn install seems default on newer hadoop versions, so switch to the old mapreduce path
        opts = {'on': ("Start Yarn instead of MapRed (SWITCHING NOT IMPLEMENTED)", None, "store_true", False),  # TODO remove when implemented
                }
        descr = ['Yarn', 'Provide Yarn related options']
        prefix = 'yarn'

        self.log.debug("Add Yarn option parser prefix %s descr %s opts %s" %
                       (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def java_options(self):
        """Some java presets"""
        opts = {'module': ("Use Java module version", "string",
                           "store", os.environ.get("EBVERSIONJAVA", ''))}
        descr = ['Java', 'Provide Java related options']
        prefix = 'java'

        self.log.debug("Add Java option parser prefix %s descr %s opts %s" %
                       (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def make_init(self):
        """Trigger all inits"""
        self.rm_options()
        self.config_options()
        self.action_options()

        self.java_options()
        self.hadoop_options()
        self.hod_options()
        self.hdfs_options()
        self.mapred_options()
        self.yarn_options()
        self.hbase_options()


if __name__ == '__main__':
    # Simple test case
    h = HodOption()
    print h.options, type(h.options)
    print h.dict_by_prefix()
    print h.generate_cmd_line()
    print h.options.debug, h.options.hbase_on
