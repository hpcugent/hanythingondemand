##
# Copyright 2009-2016 Ghent University
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
@author: Ewan Higgs (University of Ghent)
"""

import os
from errno import EEXIST
from os.path import join as mkpath

from hod.work.work import Work
from hod.config.config import env2str
from hod.commands.command import Command

class ConfiguredService(Work):
    """
    Service that reads loads a configuration and runs it.
    """
    def __init__(self, config, master_env=None):
        if master_env is None:
            master_env = dict()
        Work.__init__(self)
        self._config = config
        self._master_env = master_env
        self.name = self._config.name

    def pre_start_work_service(self):
        """Run the ExecStartPre script"""
        rank = self.svc.rank
        if len(self._config.pre_start_script) == 0:
            self.log.info('Prestarting %s service on rank %s: No work.',
                self._config.name, rank)
            return
        env = os.environ.copy()
        env.update(self._config.env)
        env.update(self._master_env)

        self.log.info('Prestarting %s service on rank %s: "%s"',
                self._config.name, rank, self._config.pre_start_script)
        command = Command(self._config.pre_start_script, env=env)
        output = command.run()
        self.log.info('Ran %s service on rank %s prestart script. Output: "%s"',
                self._config.name, rank, output)

    def start_work_service(self):
        """Start service by running the ExecStart script."""
        env = os.environ.copy()
        env.update(self._config.env)
        env.update(self._master_env)
        rank = self.svc.rank

        self.log.info('Starting %s service on rank %s: "%s"',
                self._config.name, rank, self._config.start_script)
        self.log.info("Env for %s service on rank %s: %s",
                self._config.name, rank, env2str(env))
        command = Command(self._config.start_script, env=env, timeout=self._config.timeout)
        output = command.run()
        self.log.info('Ran %s service on rank %s start script. Output: "%s"',
                self._config.name, rank, output)

    def stop_work_service(self):
        """Stop service by running the ExecStop script."""
        env = os.environ.copy()
        env.update(self._config.env)
        env.update(self._master_env)
        rank = self.svc.rank
        self.log.info('Stopping %s service on rank %s: "%s"',
            self._config.name, rank, self._config.stop_script)
        command = Command(self._config.stop_script, env=env)
        output = command.run()
        self.log.info('Ran %s service on rank %s stop script. Output: "%s"',
                self._config.name, rank, output)

    def prepare_work_cfg(self):
        """Prepare the config: collect the parameters and make the necessary xml cfg files"""
        self.controldir = mkpath(self._config.localworkdir, 'controldir')
        try:
            os.makedirs(self.controldir)
        except OSError as e:
            if e.errno == EEXIST:
                pass
            else:
                raise

    def __repr__(self):
        return 'ConfiguredService(name=%s)' % (self.name)
