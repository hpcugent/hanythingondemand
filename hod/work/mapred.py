##
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
##
"""

@author: Stijn De Weirdt
"""
import os

from hod.work.work import Work
from hod.work.hadoop import Hadoop

from hod.config.customtypes import Directories, HostnamePort
from hod.commands.hadoop import Jobtracker, Tasktracker
from hod.node import interface_to_nn


class Mapred(Hadoop):
    """Base Mapred work class"""
    def __init__(self, options):
        Work.__init__(self)  # don't use Hadoop.__init__, better to redo Hadoop.__init__ with work + opts
        self.opts = options

    def set_service_defaults(self, mis):
        """Set service specific default"""
        self.log.debug("Setting servicedefaults for %s" % mis)
        if mis in ('mapred.local.dir',):
            tmpdir = os.path.join(self.opts.basedir, 'mapredlocal')
            self.log.debug("%s not set. using  %s" % (mis, tmpdir))
            self.opts.params[mis] = Directories(tmpdir)
        elif mis in ('mapred.job.tracker',):
            intf = interface_to_nn(self.svc.thisnode, self.opts.params.get('fs.default.name'))
            if intf:
                val = HostnamePort('%s:9000' % intf[0])
                self.opts.params[mis] = val
                self.log.debug("%s not set. using  %s" % (mis, val))
            else:
                self.log.warn("could not set %s. no intf found for namenode")
        elif mis in ('mapred.map.tasks', 'mapred.tasktracker.map.tasks.maximum',):
            if mis.endswith('maximum'):
                tasks = int(len(
                    self.svc.thisnode.usablecores) / 2)  # avg 2 cores per task
            else:
                mapfactor = len(self.reduce_tasks_maximumthisnode.usablecores) * 2
                tasks = int(len(self.svc.allnodes) * mapfactor)
            self.log.debug("%s not set. using  %s" % (mis, tasks))
            self.opts.params[mis] = tasks
        elif mis in ('mapred.reduce.tasks', 'mapred.tasktracker.reduce.tasks.maximum',):
            mapfactor = 2
            if mis.endswith('maximum'):
                tasks = int(mapfactor * 1.75)  # total number of reduce tasks is maximum*number of nodes
            else:
                tasks = int(len(self.allnodes) * mapfactor)
            self.log.debug("%s not set. using  %s" % (mis, tasks))
            self.opts.params[mis] = tasks
        else:
            self.log.warn("Variable %s not found in service_defaults" %
                          mis)  # TODO is warn enough?
            return True  # not_mis_found

    def start_work_service_master(self):
        """Start service on master"""
        self.opts.set_niceness(4, 2, 3, 'socket:0')
        self.log.info("Start jobtracker service on master.")
        command = Jobtracker(self.opts.daemon_script, start=True)
        command.run()

    def start_work_service_slaves(self):
        """Run start_service on slaves"""
        self.opts.set_niceness(15, 2, 7)
        self.log.info("Start tasktracker service on slaves.")
        command = Tasktracker(self.opts.daemon_script, start=True)
        command.run()

    def stop_work_service_master(self):
        """Stop service on master"""
        self.log.info("Stop jobtracker service on master.")
        command = Jobtracker(self.opts.daemon_script, start=False)
        command.run()

    def stop_work_service_slaves(self):
        """Run start_service on slaves"""
        self.log.info("Stop tasktracker service on slaves.")
        command = Tasktracker(self.opts.daemon_script, start=False)
        command.run()
