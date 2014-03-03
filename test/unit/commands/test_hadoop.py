###
# Copyright 2009-2014 Ghent University
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
import unittest
import hod.commands.hadoop as hch

class HodCommandsHadoopTestCase(unittest.TestCase):
    def test_hadoop_command(self):
        c = hch.HadoopCommand('version')
        assert str(c) == 'hadoop version'

    def test_hadoop_version(self):
        c = hch.HadoopVersion()
        assert str(c) == 'hadoop version'

    def test_hbase_command(self):
        c = hch.HbaseCommand('version')
        assert str(c) == 'hbase version'

    def test_hbase_version(self):
        c = hch.HbaseVersion()
        assert str(c) == 'hbase version'

    def test_hadoop_daemon(self):
        c = hch.HadoopDaemon('daemon', 'hadoopcmd')
        assert str(c) == 'daemon start hadoopcmd'

    def test_namenode(self):
        c = hch.NameNode('daemon')
        assert str(c) == 'daemon start namenode'

    def test_format_hdfs(self):
        c = hch.FormatHdfs()
        assert str(c) == 'hadoop namenode -format' # 'hadoop' rather than 'daemon'.

    def test_datanode(self):
        c = hch.DataNode('daemon')
        assert str(c) == 'daemon start datanode'

    def test_jobtracker(self):
        c = hch.Jobtracker('daemon')
        assert str(c) == 'daemon start jobtracker'

    def test_tasktracker(self):
        c = hch.Tasktracker('daemon')
        assert str(c) == 'daemon start tasktracker'

    def test_hbase_zookeeper(self):
        c = hch.HbaseZooKeeper('daemon')
        assert str(c) == 'daemon start zookeeper'

    def test_hbase_master(self):
        c = hch.HbaseMaster('daemon')
        assert str(c) == 'daemon start master'

    def test_hbase_region_server(self):
        c = hch.HbaseRegionServer('daemon')
        assert str(c) == 'daemon start regionserver'
