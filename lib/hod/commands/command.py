# #
# Copyright 2009-2012 Ghent University
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
# #
"""
Command module

Taken from vsc.utils.run
-removed host functionality

TODO: acutally use vsc.utils.run here

@author: Jens Timmerman, Stijn De Weirdt
"""
from subprocess import Popen, PIPE
import datetime
import os
import signal
import time

from vsc import fancylogger


COMMAND_TIMEOUT = 120  # timeout


class Command(object):
    '''
    This class represents a command
    this will have to be extended
    '''

    def __init__(self, command=None, timeout=COMMAND_TIMEOUT):
        '''
        Constructor
        command is a string representing the command to be run
        '''
        self.log = fancylogger.getLogger(self.__class__.__name__, fname=False)
        self.command = command
        self.timeout = timeout

        self.fake_pty = False

    def __str__(self):
        cmd = self.getCommand()
        if type(cmd) in (tuple, list,):
            cmdtxt = " ".join(cmd)
        else:
            cmdtxt = str(cmd)

        return cmdtxt

    def __repr__(self):
        return str(self.getCommand())

    def getCommand(self):
        """
        shows what commands would be run
        """
        return self.command

    def run(self):
        """
        Run commands
        """
        if self.command is None:
            self.log.error("No command set")
            return

        self.log.debug("Run going to run %s" % self.command)
        start = datetime.datetime.now()

        nameds = {
            'shell': True,
            'close_fds': True,
        }
        if self.fake_pty:
            self.log.debug("Setting up PTY")
            import pty
            (master, slave) = pty.openpty()
            stdouterr = {
                'stdin': slave,
                'stdout': slave,
                'stderr': slave,
            }
        else:
            self.log.debug('Using PIPE stdout and stderr')
            stdouterr = {
                'stdout': PIPE,
                'stderr': PIPE,
            }

        nameds.update(stdouterr)
        # TODO: (high) buffer overflow here sometimes, check what happens and fix
        # see easybuild/buildsoft/async
        p = Popen(self.__str__(), **nameds)
        time.sleep(.1)  # for immediate answers
        timedout = False
        while p.poll() is None:
            if os.path.exists("/proc/%s" % (p.pid)):
                now = datetime.datetime.now()
                if (now - start).seconds > self.timeout:
                    if timedout is False:
                        os.kill(p.pid, signal.SIGTERM)
                        self.log.debug("Timeout occured with cmd %s. took more than %i secs to complete." % (self.command, self.timeout))
                        timedout = True
                    else:
                        os.kill(p.pid, signal.SIGKILL)
            time.sleep(1)

        if self.fake_pty:
            # # no stdout/stderr
            self.log.debug("No stdout/stderr in fake pty mode")
            out = 'Fake PTY no out (this is ok)'
            err = 'Fake PTY no err (this is ok)'
        else:
            out = p.stdout.read().strip()
            err = p.stderr.read().strip()

        ec = p.returncode
        if not ec == 0:
            self.log.warning("Problem occured with cmd %s: out %s, err %s" % (self.command, out, err))
            err += "Exitcode %s\n"
        else:
            self.log.debug("cmd ok %s: out %s err %s" % (self.command, out, err))
        return out, err


# # Some basic non-hadoop commands
class IpAddrShow(Command):
    """Run ip addr show"""
    def __init__(self):
        Command.__init__(self)

        ipCommand = '/sbin/ip'
        self.command = [ipCommand, "addr", "show"]


class JavaCommand(Command):
    def __init__(self, opt):
        Command.__init__(self)

        self.command = ["java", opt]


class JavaVersion(JavaCommand):
    def __init__(self):
        JavaCommand.__init__(self, '-version')

    def run(self):
        """version prints to stderr"""
        out, err = JavaCommand.run(self)
        newout = out + "\n" + err
        self.log.debug("cmd %s: %s" % (self.command, newout))
        return newout, err


class GenerateSshKey(Command):
    """Create a public/private key pair"""
    def __init__(self, key_location):
        Command.__init__(self)
        self.command = ['/usr/bin/ssh-keygen', '-t', 'rsa', '-b', '2048', '-N', '""', '-f', key_location]


class RunSshd(Command):
    def __init__(self, cfg_location):
        Command.__init__(self)
        self.command = ['/usr/sbin/sshd', '-f', cfg_location]


class KillPidFile(Command):
    def __init__(self, pid_fn):
        Command.__init__(self)
        self.pid_fn = pid_fn

    def run(self):
        fh = open(self.pid_fn)
        pid = fh.read().strip()
        fh.close()

        self.command = ['kill', pid]
        Command.run(self)


class ScreenDaemon(Command):
    """Start a named screen session in background"""
    def __init__(self, name):
        Command.__init__(self)
        # this does nto work if nothing is connected to the session
        # self.command = ['screen', '-dmS', name]
        self.command = ['screen', '-dmS', 'dummyxc', 'screen', '-S', name]
        self.fake_pty = True


class RunInScreen(Command):
    """Start a named screen session in background"""
    def __init__(self, name):
        Command.__init__(self, name)
        self.command_templ = ['screen', '-S', name, '-X', 'stuff', "$'%s\r'"]

    def run(self, command):
        self.command = self.command_templ[:]
        self.command[-1] = self.command[-1] % command
        self.log.debug("Added command %s to create real command %s" % (command, self.command))
        Command.run(self)
