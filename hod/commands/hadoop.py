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
Hadoop related commands

@author: Stijn De Weirdt
"""

from hod.commands.command import Command


class HadoopCommand(Command):
    def __init__(self, opt):
        Command.__init__(self)

        cmds = ['hadoop', opt]
        self.command = " ".join(cmds)


class HadoopVersion(HadoopCommand):
    def __init__(self):
        HadoopCommand.__init__(self, 'version')


class HbaseCommand(Command):
    def __init__(self, opt):
        Command.__init__(self)

        cmds = ['hbase', opt]
        self.command = " ".join(cmds)


class HbaseVersion(HbaseCommand):
    def __init__(self):
        HbaseCommand.__init__(self, 'version')


class HadoopDaemon(Command):
    def __init__(self, daemon, hadoopcmd, args=[], start=True, cfg=None):
        Command.__init__(self)
        cmds = [daemon]
        if cfg:
            cmds += ['--config', cfg]
        if start:
            cmds += ['start']
        else:
            cmds += ['stop']

        cmds += [hadoopcmd]
        cmds += args

        self.command = " ".join(cmds)


class NameNode(HadoopDaemon):
    """The namenode command"""
    def __init__(self, daemon, start=True):
        HadoopDaemon.__init__(self, daemon, 'namenode', start=start)


class FormatHdfs(HadoopCommand):
    """Format the DFS filesystem command"""
    def __init__(self):
        HadoopCommand.__init__(self, 'namenode -format')


class DataNode(HadoopDaemon):
    """The datanode command"""
    def __init__(self, daemon, start=True):
        HadoopDaemon.__init__(self, daemon, 'datanode', start=start)


class Jobtracker(HadoopDaemon):
    """The jobtracker command"""
    def __init__(self, daemon, start=True):
        HadoopDaemon.__init__(self, daemon, 'jobtracker', start=start)


class Tasktracker(HadoopDaemon):
    """The tasktracker command"""
    def __init__(self, daemon, start=True):
        HadoopDaemon.__init__(self, daemon, 'tasktracker', start=start)


class HbaseZooKeeper(HadoopDaemon):
    """The hbase zookeeper command"""
    def __init__(self, daemon, start=True):
        HadoopDaemon.__init__(self, daemon, 'zookeeper', start=start)


class HbaseMaster(HadoopDaemon):
    """The hbase master command"""
    def __init__(self, daemon, start=True):
        HadoopDaemon.__init__(self, daemon, 'master', start=start)


class HbaseRegionServer(HadoopDaemon):
    """The regionserver command"""
    def __init__(self, daemon, start=True):
        HadoopDaemon.__init__(self, daemon, 'regionserver', start=start)
