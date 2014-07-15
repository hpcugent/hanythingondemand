# #
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
# #
"""

@author: Stijn De Weirdt
"""
import os
from os.path import join as mkpath, basename

from hod.commands.command import Command
from hod.mpiservice import MpiService, Task, MASTERRANK
from hod.config.config import (PreServiceConfigOpts, ConfigOpts, expanded_path,
        TemplateResolver, env2str)
from hod.work.config_service import ConfiguredService

from vsc.utils import fancylogger
_log = fancylogger.getLogger(fname=False)

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
    except OSError:
        pass


def _copy_config(src_file, dest_dir, resolver):
    cfg = open(src_file, 'r').read()
    cfg = resolver(cfg)
    dest_file = mkpath(dest_dir, basename(src_file))
    open(dest_file, 'w').write(cfg)

def _setup_config_paths(precfg, resolver):
    """
    Make the base and config directories; copy target service (i.e. hadoop xml)
    config into config dir.

    This needs to happen on master and slave nodes.
    """
    _ignore_oserror(lambda: os.makedirs(precfg.basedir))
    _ignore_oserror(lambda: os.makedirs(precfg.configdir))
    for d in precfg.directories:
        _ignore_oserror(lambda: os.makedirs(expanded_path(d)))

    _log.info("Copying %d config files to %s" % (len(precfg.config_files), precfg.configdir))
    for cfg in precfg.config_files:
        _log.info("Copying config %s file to '%s'" % (cfg, precfg.configdir))
        _copy_config(cfg, precfg.configdir, resolver)


class ConfiguredMaster(MpiService):
    """
    Use config to setup services.
    """
    def __init__(self, options):
        MpiService.__init__(self)
        self.options = options

    def distribution(self, **master_template_kwargs):
        """Master makes the distribution"""
        resolver = TemplateResolver(**master_template_kwargs)

        self.tasks = []
        m_config_filename = self.options.options.config_config
        self.log.info('Loading "%s" manifest config'  % m_config_filename)

        m_config = PreServiceConfigOpts(open(m_config_filename, 'r'), resolver.workdir)

        _setup_config_paths(m_config, resolver)

        master_env = dict([(v, os.getenv(v)) for v in m_config.master_env])
        self.log.debug('MasterEnv is: %s' % env2str(master_env))

        svc_cfgs = m_config.service_files
        self.log.info('Loading %d service configs.'  % len(svc_cfgs))
        for config_filename in svc_cfgs:
            self.log.info('Loading "%s" service config'  % config_filename)
            config = ConfigOpts(open(config_filename, 'r'), resolver)
            ranks_to_run = config.runs_on(MASTERRANK, range(self.size))
            self.log.debug('Adding ConfiguredService Task to work with config: %s' % str(config))
            self.tasks.append(Task(ConfiguredService, ranks_to_run, config, master_env))


class ConfiguredSlave(MpiService):
    """
    Use config to setup services.
    """
    def __init__(self, options):
        MpiService.__init__(self)
        self.options = options

    def distribution(self, **master_template_kwargs):
        """
        Master makes the distribution

        This only needs to run if there are more than 1 node (self.size>1)
        """
        resolver = TemplateResolver(**master_template_kwargs)

        m_config_filename = self.options.options.config_config
        self.log.info('Loading "%s" manifest config'  % m_config_filename)
        m_config = PreServiceConfigOpts(open(m_config_filename, 'r'), resolver.workdir)

        _setup_config_paths(m_config, resolver)
