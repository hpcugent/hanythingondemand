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
from hod.config.hdfs import HdfsOpts

from hod.config.customtypes import HostnamePort, Directories
from hod.commands.hadoop import NameNode, DataNode, FormatHdfs


class Hdfs(HdfsOpts, Hadoop):
    """Base Hdfs work class"""
    def __init__(self, ranks, shared):
        Work.__init__(self, ranks)  # don't use Hadoop.__init__, better to redo Hadoop.__init__ with work + opts
        HdfsOpts.__init__(self, shared)

    def set_service_defaults(self, mis):
        """Set service specific default"""
        self.log.debug("Setting servicedefaults for %s" % mis)
        if mis in ('dfs.name.dir', 'dfs.data.dir',):
            tmpdir = os.path.join(self.basedir, mis)
            self.log.debug("%s not set. using  %s" % (mis, tmpdir))
            self.params[mis] = Directories(tmpdir)
        elif mis in ('dfs.datanode.address',):
            intf = self.interface_to_nn()
            if intf:
                val = HostnamePort('%s:50090' % intf[0])
                self.params[mis] = val
                self.log.debug("%s not set. using  %s" % (mis, val))
            else:
                self.log.warn("could not set %s. no intf found for namenode")
        elif mis in ('dfs.datanode.ipc.address',):
            intf = self.interface_to_nn()
            if intf:
                val = HostnamePort('%s:50020' % intf[0])
                self.params[mis] = val
                self.log.debug("%s not set. using  %s" % (mis, val))
            else:
                self.log.warn("could not set %s. no intf found for namenode")
        else:
            self.log.warn("Variable %s not found in service defaults" %
                          mis)  # TODO is warn enough?
            return True  # not_mis_found

    def start_work_service_master(self):
        """Start service on master"""
        self.set_niceness(1, 2, 0, 'socket:0')
        if self.format_hdfs:
            self.log.info("Formatting HDFS")
            name_dir = self.params.get('dfs.name.dir', None)
            if name_dir:
                dest_dir = "%s.renamebeforeformat" % name_dir
                self.log.debug('Namedir %s found during format. Going to rename it to %s.' % (name_dir, dest_dir))
                os.rename("%s" % name_dir, dest_dir)

            formatcommand = FormatHdfs()
            formatcommand.run()
        else:
            self.log.debug("No HDFS format")

        self.log.info("Start namenode service on master.")
        command = NameNode(self.daemon_script, start=True)
        command.run()

    def start_work_service_slaves(self):
        """Run start_service on slaves"""
        self.set_niceness(5, 2, 3, 'socket:0')
        self.log.info("Start datanode service on slaves.")
        command = DataNode(self.daemon_script, start=True)
        command.run()

    def stop_work_service_master(self):
        """Stop service on master"""
        self.log.info("Stop namenode service on master.")
        command = NameNode(self.daemon_script, start=False)
        command.run()

    def stop_work_service_slaves(self):
        """Run start_service on slaves"""
        self.log.info("Stop datanode service on slaves.")
        command = DataNode(self.daemon_script, start=False)
        command.run()
