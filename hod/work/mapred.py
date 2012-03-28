from hod.work.work import Work
from hod.work.hadoop import Hadoop
from hod.config.mapred import MapredOpts

from vsc import fancylogger
fancylogger.setLogLevelDebug()


class Mapred(MapredOpts, Hadoop):
    """Base Mapred work class"""
    def __init__(self, ranks):
        Work.__init__(self, ranks)  ## don't use Hadoop.__init__, better to redo Hadoop.__init__ with work + opts
        MapredOpts.__init__(self)
