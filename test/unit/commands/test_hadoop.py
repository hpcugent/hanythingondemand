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
