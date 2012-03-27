"""
Command module

Taken from Jens Timmerman managecommands
-removed host functionality
"""
from subprocess import Popen, PIPE
import datetime
import os
import signal
import time

from vsc import fancylogger
fancylogger.setLogLevelDebug()


COMMAND_TIMEOUT = 120 ## timeout

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
        self.log = fancylogger.getLogger(self.__class__.__name__)
        self.command = command
        self.timeout = timeout

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
        #TODO: (high) buffer overflow here sometimes, check what happens and fix
        #see easybuild/buildsoft/async 
        p = Popen(self.__str__(), shell=True, stdout=PIPE, stderr=PIPE, close_fds=True)
        time.sleep(.1) ## for immediate answers
        timedout = False
        while p.poll() is None:
            if os.path.exists("/proc/%s" % (p.pid)):
                now = datetime.datetime.now()
                if (now - start).seconds > self.timeout:
                    if timedout == False:
                        os.kill(p.pid, signal.SIGTERM)
                        self.log.debug("Timeout occured with cmd %s. took more than %i secs to complete." % (self.command, self.timeout))
                        timedout = True
                    else:
                        os.kill(p.pid, signal.SIGKILL)
            time.sleep(1)

        out = p.stdout.read().strip()
        err = p.stderr.read().strip()

        ec = p.returncode
        if not ec == 0:
            self.log.warning("Problem occured with cmd %s: out %s, err %s" % (self.command, out, err))
            err += "Exitcode %s\n"
        else:
            self.log.debug("cmd %s: %s" % (self.command, out))
        return out, err


## Some basic non-hadoop commands
class IpAddrShow(Command):
    """Run ip addr show"""
    def __init__(self):
        Command.__init__(self)

        ipCommand = '/sbin/ip'
        self.command = [ipCommand, "addr", "show"]
