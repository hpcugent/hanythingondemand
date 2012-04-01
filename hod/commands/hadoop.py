"""
Hadoop related commands
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
    """The datanode command"""
    def __init__(self, daemon, start=True):
        HadoopDaemon.__init__(self, daemon, 'jobtracker', start=start)

class Tasktracker(HadoopDaemon):
    """The datanode command"""
    def __init__(self, daemon, start=True):
        HadoopDaemon.__init__(self, daemon, 'tasktracker', start=start)

