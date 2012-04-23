
#
# Copyright 2012 Stijn De Weirdt
# 
# This file is part of HanythingOnDemand,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
from vsc import fancylogger
fancylogger.setLogLevelDebug()

import sys, re

from hod.config.generaloption import GeneralOption

class HodOption(GeneralOption):
    def rm_options(self):
        """Make the rm related options"""
        opts = {"walltime":("Job walltime in hours", 'float', 'store', 48, 'l'),
                "nodes":("Full nodes for the job", "int", "store", 5, "n"),
                "ppn":("Processors per node (-1=full node)", "int", "store", -1),
                "mail":("When to send mail (b=begin, e=end, a=abort)", "string", "extend", [], "m"),
                "mailothers":("Other email adresses to send mail to", "string", "extend", [], "M"),
                "name":("Job name", "string", "store", "HanythingOnDemand_job", "N"),
                "queue":("Queue name (empty string is default queue)", "string", "store", "", "q"),
              }
        descr = ["Resource manager / Scheduler", "Provide resource manager/scheduler related options (eg number of nodes)"]

        prefix = 'rm'
        self.log.debug("Add resourcemanager option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def action_options(self):
        """Make the action related options"""
        opts = {"create":("Create and submit new HOD job", None, "store_true", False, 'C'),
                "showall":("Show info on all found HOD jobs (this is the default action)", None, "store_true", True),
                #"showjob":("Show info for HOD job JOBID", "string", "store", ''),
                #"removejob":("Remove HOD job JOBID", "string", "store", ''),
              }
        descr = ["Action", "What action to take"]

        prefix = 'action'
        self.log.debug("Add action option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)


    def hdfs_options(self):
        """Some hdfs presets"""
        opts = {'off':("Don't start HDFS", None, "store_true", False),
                }
        descr = ['HDFS', 'Provide HDFS related options']
        prefix = 'hdfs'

        self.log.debug("Add HDFS option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def mapred_options(self):
        """Some mapred presets"""
        opts = {'off':("Don't start MapRed (MR1)", None, "store_true", False),
                }
        descr = ['MapReduce', 'Provide MapReduce (MR1) related options']
        prefix = 'mr1'

        self.log.debug("Add MapRed option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def hadoop_options(self):
        """Some hadoop presets"""
        opts = {
                'module':("Use Hadoop module version", "string", "store", "0.20.2-cdh3u3"),
                }
        descr = ['Hadoop', 'Provide Hadoop related options']
        prefix = 'hadoop'

        self.log.debug("Add Hadoop option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def hod_options(self):
        """Some HOD presets"""
        opts = {
                'envclass':("Use HodJob class to create working enviromnet", "string", "store", ""),
                'envscript':("Use script to create working enviromnet", "string", "store", ""),
                'script':("Run this script as start of local client screen session", "string", "store", ''),
                }
        descr = ['HOD', 'Provide HOD related options']
        prefix = 'hod'

        self.log.debug("Add Hod option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)


    def hbase_options(self):
        """Some hbase presets"""
        opts = {'on':("Start HBase", None, "store_true", False),
                'module':("Use HBase module version", "string", "store", "0.90.4-cdh3u3"),
                }
        descr = ['HBase', 'Provide HBase related options']
        prefix = 'hbase'

        self.log.debug("Add HBase option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)

    def yarn_options(self):
        """Some hbase presets"""
        opts = {'on':("Start Yarn instead of MapRed (NOT IMPLEMENTED)", None, "store_true", False), ## TODO remove when implemented
                }
        descr = ['Yarn', 'Provide Yarn related options']
        prefix = 'yarn'

        self.log.debug("Add Yarn option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)


    def java_options(self):
        """Some java presets"""
        opts = {'module':("Use Java module version", "string", "store", "1.7.0_3"),
                }
        descr = ['Java', 'Provide Java related options']
        prefix = 'java'

        self.log.debug("Add Java option parser prefix %s descr %s opts %s" % (prefix, descr, opts))
        self.add_group_parser(opts, descr, prefix=prefix)


    def make_init(self):
        """Trigger all inits"""
        self.rm_options()
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


