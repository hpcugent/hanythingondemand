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
@author: Ewan Higgs
"""

import os
import pwd
from tempfile import mkdtemp
from os.path import join as mkpath, basename

from hod.work.work import Work
from hod.config.config import resolve_config_str
from hod.commands.command import Command

def _ignore_oserror(fn):
    '''
    Given a function, ignore OSError. 
    >>> def fn(x,y):
    ...    raise OSError
    >>> _ignore_oserror(lambda: fn(1,2))
    >>>
    '''
    try:
        fn()
    except OSError, e:
        pass

class ConfiguredService(Work):
    """
    Work that reads loads a configuration and runs it.
    """
    def __init__(self, config):
        Work.__init__(self)
        self._config = config

    def start_work_service_master(self):
        """Start service on master"""
        self._config.setenv()
        self.log.info('Running to start %s service on master: "%s"' %
                (self._config.name, self._config.start_script))
        self.log.info("Env for %s service on master: %s" % (self._config.name,
            self._config.env))
        command = Command(self._config.start_script)
        output = command.run()
        self.log.info('Ran %s service master startscript. Output: "%s"' % output)

    def start_work_service_slaves(self):
        """Run start_service on slaves"""
        self._config.setenv()
        self.log.info('Running to start %s service on slaves: "%s"' %
            (self._config.name, self._config.start_script))
        self.log.info("Env for %s service on slaves : %s" % (self._config.name,
            self._config.env))
        command = Command(self._config.start_script)
        output = command.run()
        self.log.info('Ran %s service slave start script. Output: "%s"' % output)

    def stop_work_service_master(self):
        """Stop service on master"""
        self._config.setenv()
        self.log.info('Running to stop %s service on master: "%s"' %
            (self._config.name, self._config.stop_script))
        command = Command(self._config.stop_script)
        output = command.run()
        self.log.info('Ran %s service master stop script. Output: "%s"' % output)

    def stop_work_service_slaves(self):
        """Run start_service on slaves"""
        self._config.setenv()
        self.log.info('Running to stop %s service on slaves: "%s"' %
            (self._config.name, self._config.stop_script))
        command = Command(self._config.stop_script)
        output = command.run()
        self.log.info('Ran %s service slave stop script. Output: "%s"' % output)

    def prepare_work_cfg(self):
        """prepare the config: collect the parameters and make the necessary xml cfg files"""
        _ignore_oserror(lambda: os.makedirs(self._config.basedir))
        _ignore_oserror(lambda: os.makedirs(self._config.configdir))
        if self._config.config_file:
            work_config = open(self._config.config_file, 'r').read()
            work_config = resolve_config_str(work_config)
            dest = mkpath(self._config.configdir, basename(self._config.config_file))
            self.log.info("Writing config file to '%s'" % dest)
            open(dest, 'w').write(work_config)
        # set the controldir to the confdir
        self.controldir = mkdtemp(prefix='controldir', dir=self._config.basedir)

class ScreenService(Work):
    """
    Run screen command.
    """
    def __init__(self, config):
        Work.__init__(self)
        self._config = config

    def start_work_service_master(self):
        self.log.info('Starting ScreenService')

    def start_work_service_slaves(self):
        pass
    def stop_work_service_master(self):
        pass
        self.log.info('Stopping ScreenService')

    def stop_work_service_slaves(self):
        pass

class SSHService(Work):
    """
    Run ssh command.
    """
    def __init__(self, config):
        Work.__init__(self)
        self._config = config

    def start_work_service_master(self):
        self.log.info('Starting SSHService')

    def start_work_service_slaves(self):
        pass

    def stop_work_service_master(self):
        pass
        self.log.info('Stopping SSHService')

    def stop_work_service_slaves(self):
        pass


