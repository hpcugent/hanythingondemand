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

@author: Stijn De Weirdt (Ghent University)
"""
import os
from errno import EEXIST
from os.path import join as mkpath
from hod.mpiservice import MpiService, Task, MASTERRANK, ConfigOptsParams
from hod.config.config import (PreServiceConfigOpts, ConfigOpts,
        env2str, service_config_fn, write_service_config,
        preserviceconfigopts_from_file_list, parse_comma_delim_list)
from hod.config.template import (TemplateRegistry, TemplateResolver,
        register_templates)
from hod.work.config_service import ConfiguredService

from vsc.utils import fancylogger
_log = fancylogger.getLogger(fname=False)

def _ignore_eexist(fn):
    '''
    Given a function, ignore errors where files already exist.
    '''
    try:
        fn()
    except OSError, e:
        if e.errno == EEXIST:
            pass
        else:
            raise

def _setup_config_paths(precfg, resolver):
    """
    Make the base and config directories; copy target service (i.e. hadoop xml)
    config into config dir.

    This needs to happen on master and slave nodes.
    """
    _ignore_eexist(lambda: os.makedirs(precfg.workdir))
    _ignore_eexist(lambda: os.makedirs(precfg.configdir))
    for d in precfg.directories:
        _ignore_eexist(lambda: os.makedirs(resolver(d)))

    _log.info("Looking up config_writer %s", len(precfg.config_writer))
    config_writer = service_config_fn(precfg.config_writer)

    _log.info("Copying %d config files to %s", len(precfg.service_configs), precfg.configdir)
    for dest_file, cfg in precfg.service_configs.items():
        _log.info("Copying config %s file to '%s'", cfg, precfg.configdir)
        dest_path = mkpath(precfg.configdir, dest_file)
        write_service_config(dest_path, cfg, config_writer, resolver)

def _load_manifest_config(filenames, workdir, modules):
    '''
    Load the manifest config (hod.conf) files.
    '''
    m_config_filenames = parse_comma_delim_list(filenames)
    _log.info('Loading "%s" manifest config', m_config_filenames)
    m_config = preserviceconfigopts_from_file_list(m_config_filenames,
            workdir=workdir, modules=modules)
    _log.debug('Loaded manifest config: %s', str(m_config))
    return m_config

def _setup_template_resolver(m_config, master_template_args):
    '''
    Build a template resovler using the template args from the master node.
    '''
    reg = TemplateRegistry()
    register_templates(reg, m_config)
    for ct in master_template_args:
        reg.register(ct)
    return TemplateResolver(**reg.to_kwargs())

class ConfiguredMaster(MpiService):
    """
    Use config to setup services.
    """
    def __init__(self, options):
        MpiService.__init__(self)
        self.options = options

    def distribution(self, *master_template_args, **kwargs):
        """Master makes the distribution"""
        self.tasks = []
        m_config = _load_manifest_config(self.options.options.config_config,
                self.options.options.config_workdir, 
                self.options.options.config_modules)
        m_config.autogen_configs()

        resolver = _setup_template_resolver(m_config, master_template_args)
        _setup_config_paths(m_config, resolver)

        master_env = dict([(v, os.getenv(v)) for v in m_config.master_env])
        self.log.debug('MasterEnv is: %s', env2str(master_env))

        svc_cfgs = m_config.service_files
        self.log.info('Loading %d service configs.', len(svc_cfgs))
        for config_filename in svc_cfgs:
            self.log.info('Loading "%s" service config', config_filename)
            config = ConfigOpts(open(config_filename, 'r'), resolver)
            ranks_to_run = config.runs_on(MASTERRANK, range(self.size))
            self.log.debug('Adding ConfiguredService Task to work with config: %s',
                    str(config))
            cfg_opts = ConfigOptsParams(config_filename, m_config.workdir, m_config.modules, master_template_args)
            self.tasks.append(Task(ConfiguredService, config.name, ranks_to_run, cfg_opts, master_env))

class ConfiguredSlave(MpiService):
    """
    Use config to setup services.
    """
    def __init__(self, options):
        MpiService.__init__(self)
        self.options = options

    def distribution(self, *master_template_args, **kwargs):
        """
        Master makes the distribution

        This only needs to run if there are more than 1 node (self.size>1)
        """
        m_config = _load_manifest_config(self.options.options.config_config,
                self.options.options.config_workdir,
                self.options.options.config_modules)
        m_config.autogen_configs()
        resolver = _setup_template_resolver(m_config, master_template_args)
        _setup_config_paths(m_config, resolver)
