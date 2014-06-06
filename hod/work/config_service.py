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

    def pre_start_work_service(self):
        env = self._config.envstr()
        rank = self.svc.rank

        if len(self._config.pre_start_script) == 0:
            self.log.info('Prestarting %s service on rank %s: No work.' %
                (self._config.name, rank))
            return

        self.log.info('Prestarting %s service on rank %s: "%s"' %
                (self._config.name, rank, self._config.pre_start_script))
        command = Command('%s %s' % (env, self._config.pre_start_script))
        output = command.run()
        self.log.info('Ran %s service on rank %s prestart script. Output: "%s"' %
                (self._config.name, rank, output))


    def start_work_service(self):
        """Start service on master"""
        env = self._config.envstr()
        rank = self.svc.rank

        self.log.info('Starting %s service on rank %s: "%s"' %
                (self._config.name, rank, self._config.start_script))
        self.log.info("Env for %s service on rank %s: %s" % 
                (self._config.name, rank, env))
        command = Command('%s %s' % (env, self._config.start_script))
        output = command.run()
        self.log.info('Ran %s service on rank %s start script. Output: "%s"' % 
                (self._config.name, rank, output))

    def stop_work_service(self):
        """Stop service on master"""
        env = self._config.envstr()
        rank = self.svc.rank
        self.log.info('Stopping %s service on rank %s: "%s"' %
            (self._config.name, rank, self._config.stop_script))
        command = Command('%s %s' % (env, self._config.stop_script))
        output = command.run()
        self.log.info('Ran %s service on rank %s stop script. Output: "%s"' % 
                (self._config.name, rank, output))

    def prepare_work_cfg(self):
        """prepare the config: collect the parameters and make the necessary xml cfg files"""
        # set the controldir to the confdir
        self.controldir = mkdtemp(prefix='controldir', dir=self._config.basedir)
