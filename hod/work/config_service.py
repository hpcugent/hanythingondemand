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
from hod.commands.command import Command

class ConfiguredService(Work):
    """
    Work that reads loads a configuration and runs it.
    """
    def __init__(self, config):
        Work.__init__(self)
        self._config = config

    def start_work_service_master(self):
        """Start service on master"""
        env = self._config.envstr()
        self.log.info('Running to start %s service on master: "%s"' %
                (self._config.name, self._config.start_script))
        self.log.info("Env for %s service on master: %s" % (self._config.name, env))
        command = Command('%s %s' % (env, self._config.start_script))
        output = command.run()
        self.log.info('Ran %s service master startscript. Output: "%s"' % output)

    def start_work_service_slaves(self):
        """Run start_service on slaves"""
        env = self._config.envstr()
        self.log.info('Running to start %s service on slaves: "%s"' %
            (self._config.name, self._config.start_script))
        self.log.info("Env for %s service on slaves: %s" % (self._config.name, env))
        command = Command('%s %s' % (env, self._config.start_script))
        output = command.run()
        self.log.info('Ran %s service slave start script. Output: "%s"' % output)

    def stop_work_service_master(self):
        """Stop service on master"""
        env = self._config.envstr()
        self.log.info('Running to stop %s service on master: "%s"' %
            (self._config.name, self._config.stop_script))
        command = Command('%s %s' % (env, self._config.stop_script))
        output = command.run()
        self.log.info('Ran %s service master stop script. Output: "%s"' % output)

    def stop_work_service_slaves(self):
        """Run start_service on slaves"""
        env = self._config.envstr()
        self.log.info('Running to stop %s service on slaves: "%s"' %
            (self._config.name, self._config.stop_script))
        command = Command('%s %s' % (env, self._config.stop_script))
        output = command.run()
        self.log.info('Ran %s service slave stop script. Output: "%s"' % output)

    def prepare_work_cfg(self):
        """prepare the config: collect the parameters and make the necessary xml cfg files"""
        # set the controldir to the confdir
        self.controldir = mkdtemp(prefix='controldir', dir=self._config.basedir)
