from hod.work.work import Work
from hod.work.hadoop import Hadoop
from hod.config.hdfs import HdfsOpts

from vsc import fancylogger
fancylogger.setLogLevelDebug()


class Hdfs(HdfsOpts, Hadoop):
    """Base Hdfs work class"""
    def __init__(self, ranks):
        Work.__init__(self, ranks) ## don't use Hadoop.__init__, better to redo Hadoop.__init__ with work + opts
        HdfsOpts.__init__(self)
