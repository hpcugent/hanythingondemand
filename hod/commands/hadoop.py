"""
Hadoop related commands
"""

from hod.commands.command import Command



class HadoopCommand(Command):
    def __init__(self, opt):
        Command.__init__(self)

        self.command = "hadoop %s" % opt


class HadoopVersion(HadoopCommand):
    def __init__(self):
        HadoopCommand.__init__(self, 'version')


