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
@author: Ewan Higgs
"""

from ConfigParser import SafeConfigParser, NoOptionError
import socket
import string
from collections import OrderedDict
import os
import pwd
from os.path import join as mkpath, realpath, dirname
from functools import partial
from importlib import import_module
import hod.node as node

# hod manifest config sections
_META_SECTION = 'Meta'
_CONFIG_SECTION = 'Config'

# serviceaconfig sections
_UNIT_SECTION = 'Unit'
_SERVICE_SECTION = 'Service'
_ENVIRONMENT_SECTION = 'Environment'

RUNS_ON_MASTER = 0x1
RUNS_ON_SLAVE = 0x2
RUNS_ON_ALL = RUNS_ON_MASTER | RUNS_ON_SLAVE

def _templated_strings(workdir):
    '''
    Return the template dict with the name fed through.
    This will include environment variables.
    '''
    localworkdir = _mklocalworkdir(workdir)
    local_data_network = node.sorted_network(node.get_networks())[0]
    _strings = {
         #'masterhostname': This value is passed in.
         #'masterdatahostname': This value is passed in.
        'hostname': socket.getfqdn,
        'hostaddress': lambda: socket.gethostbyname(socket.getfqdn()),
        'datahostname' : local_data_network.hostname,
        'dataaddr' : local_data_network.addr,
        'workdir': workdir,
        'localworkdir': localworkdir,
        'user': _current_user,
        'pid': os.getpid,
        }
    _strings.update(os.environ)

    return _strings

def load_service_config(fileobj):
    '''
    Load a .ini style config for a service.
    '''
    config = SafeConfigParser()
    # optionxform = Option Transform; using str stops making it lower case.
    config.optionxform = str
    config.readfp(fileobj)
    return config

def _resolve_templates(templates):
    '''
    Take a dict of string to either string or to a nullary function and
    return the resolved data
    '''
    v = [v if not callable(v) else v() for k,v in templates.items()]
    return dict(zip(templates.keys(), v))

def resolve_config_str(s, template_dict, **template_kwargs):
    '''
    Given a string, resolve the templates based on template_dict and
    template_kwargs.
    '''
    template = string.Template(s)
    template_strings = template_dict.copy()
    template_strings.update(template_kwargs)
    resolved_templates = _resolve_templates(template_strings)
    return template.substitute(**resolved_templates)

def _current_user():
    '''
    Return the current user name as recommended by documentation of
    os.getusername.
    '''
    return pwd.getpwuid(os.getuid()).pw_name

def _mklocalworkdir(workdir):
    '''
    Construct the pathname for a workdir with a path local to this
    host/job/user.
    '''
    user = _current_user()
    pid = os.getpid()
    hostname = socket.getfqdn()
    dir_name = ".".join([user, hostname, str(pid)])
    return mkpath(workdir, 'hod', dir_name)

def _abspath(filepath, working_dir):
    '''
    Take a filepath and working_dir and return the absolute path for the
    filepath. If the filepath is already absolute then just return it.
    '''
    if not len(filepath):
        return realpath(working_dir)
    elif filepath[0] == '/': # filepath is already absolute
        return filepath

    return realpath(mkpath(working_dir, filepath))

def _fileobj_dir(fileobj):
    if hasattr(fileobj, 'name'):
        return dirname(fileobj.name)
    return ''

def _parse_runs_on(s):
    '''True if master; False if slave. Error otherwise.'''

    if s.lower() == 'master':
        return RUNS_ON_MASTER
    elif s.lower() == 'slave':
        return RUNS_ON_SLAVE
    elif s.lower() == 'all':
        return RUNS_ON_ALL
    else:
        raise ValueError('runs-on field must be either "master" or "slave".')

def _parse_comma_delim_list(s):
    '''
    Convert a string containing a comma delimited list into a list of strings
    with no spaces on the end or beginning.
    '''
    return [x.strip() for x in s.split(',')]


class TemplateResolver(object):
    '''
    Resolver for templates. This is partially applied wrapper around
    resolve_config_str but picklable.
    '''
    def __init__(self, **template_kwargs):
        self.workdir = template_kwargs['workdir'] # raise if not found...
        self._template_kwargs = template_kwargs

    def __call__(self, s):
        '''Given a string with template placeholders, return the resolved string'''
        _template = _templated_strings(self.workdir)
        return resolve_config_str(s, _template, **self._template_kwargs)


class PreServiceConfigOpts(object):
    r"""
    Manifest file for the group of services responsible for defining service
    level configs which need to be run through the template before any services
    can begin.
    """
    __slots__ = ['version', 'workdir', 'localworkdir', 'configdir',
            'config_writer', 'directories', 'modules', 'service_configs',
            'service_files', 'master_env']
    def __init__(self, fileobj):
        _config = load_service_config(fileobj)
        self.version = _config.get(_META_SECTION, 'version')
        self.workdir = _config.get(_CONFIG_SECTION, 'workdir')
        self.localworkdir = _mklocalworkdir(self.workdir)
        self.configdir = mkpath(self.localworkdir, 'conf')

        fileobj_dir = _fileobj_dir(fileobj)

        def _fixup_path(cfg):
            return _abspath(cfg, fileobj_dir)

        self.modules = _parse_comma_delim_list(_config.get(_CONFIG_SECTION, 'modules'))
        self.master_env = _parse_comma_delim_list(_config.get(_CONFIG_SECTION, 'master_env'))
        self.service_files = _parse_comma_delim_list(_config.get(_CONFIG_SECTION, 'services'))
        self.service_files = [_fixup_path(cfg) for cfg in self.service_files]
        self.directories = _parse_comma_delim_list(_config.get(_CONFIG_SECTION, 'directories'))
        if _config.has_option(_CONFIG_SECTION, 'config_writer'):
            self.config_writer= _config.get(_CONFIG_SECTION, 'config_writer')
            self.service_configs = self._collect_configs(_config)
        else:
            def _noop(*args): pass
            self.config_writer = _noop
            self.service_configs = dict()

    def _collect_configs(self, config):
        """Convert sections into dicts of options"""
        service_configs = dict()
        for section in [s for s in config.sections() if s not in [_META_SECTION, _CONFIG_SECTION]]:
            option_dict = dict()
            options = config.options(section)
            for option in options:
                option_dict[option] = config.get(section, option)

            service_configs[section] = option_dict

        return service_configs


def _cfgget(config, section, item, dflt=None):
    '''Get a value from a ConfigParser object or a default if it's not there.'''
    if dflt is None:
        return config.get(section, item)
    try:
        return config.get(section, item)
    except NoOptionError:
        return dflt

def env2str(env):
    '''
    Take a dict of environment variable names mapped to their values and
    convert it to a string that can be used to prepend a command.
    '''
    envstr = ''
    for k, v in env.items():
        envstr += '%s=%s ' % (k, v)
    return envstr



class ConfigOpts(object):
    r"""
    Wrapper for the service configuration.
    Each of the config values can have a $variable which will be replaces
    by the value in the template strings except 'name'. Name cannot be
    templated.

    Some of the slots are computed on call so that they can run on the Slave
    nodes as opposed to the Master nodes.
    """
    def __init__(self, fileobj, template_resolver):
        self._config = load_service_config(fileobj)
        self.name = _cfgget(self._config, _UNIT_SECTION, 'Name')
        self._runs_on = _parse_runs_on(_cfgget(self._config, _UNIT_SECTION, 'RunsOn'))
        self._tr = template_resolver


    @property
    def pre_start_script(self): 
        return self._tr(_cfgget(self._config, _SERVICE_SECTION, 'ExecStartPre', ''))

    @property
    def start_script(self): 
        return self._tr(_cfgget(self._config, _SERVICE_SECTION, 'ExecStart'))

    @property
    def stop_script(self):
        return self._tr(_cfgget(self._config, _SERVICE_SECTION, 'ExecStop'))

    @property
    def workdir(self): 
        return self._tr.workdir

    @property
    def localworkdir(self): 
        return _mklocalworkdir(self._tr.workdir)

    @property
    def configdir(self): 
        return mkpath(self.localworkdir, 'conf')

    @property
    def env(self):
        return OrderedDict([(k, self._tr(v)) for k, v in self._config.items(_ENVIRONMENT_SECTION)])

    def runs_on(self, masterrank, ranks):
        '''
        Given the master rank and all ranks, return a list of the ranks this
        service will run on.
        '''
        if self._runs_on == RUNS_ON_MASTER:
            return [masterrank]
        elif self._runs_on == RUNS_ON_SLAVE:
            return [x for x in ranks if x != masterrank]
        elif self._runs_on == RUNS_ON_ALL:
            return ranks
        else:
            raise ValueError('ConfigOpts.runs_on has invalid value: %s' %
                    self._runs_on)

    def __str__(self):
        return 'ConfigOpts(name=%s, runs_on=%d, pre_start_script=%s, ' \
                'start_script=%s, stop_script=%s, workdir=%s, localworkdir=%s)' %  (self.name,
                self._runs_on, self.pre_start_script, self.start_script,
                self.stop_script, self.workdir, self.localworkdir)
    def __repr__(self):
        return 'ConfigOpts(name=%s, runs_on=%d)' % (self.name, self._runs_on)

    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)


def service_config_fn(policy_path):
    """
    Given a module string ending in a function name, return the relevant
    function.
    Params
    ------
    policy_path : `str`
    Dotted string path of module. e.g. 'hod.config.write_policy.hadoop_xml'

    Returns
    -------
    function taking dict and TemplateResolver
    """
    policy_path_list = policy_path.split('.')
    module_path = '.'.join(policy_path_list[0:-1])
    fn = policy_path_list[-1]
    module = import_module(module_path)
    return getattr(module, fn)

def write_service_config(outfile, data_dict, config_writer, template_resolver):
    """Write service config files to disk."""
    with open(outfile, 'w') as f:
        f.write(config_writer(data_dict, template_resolver))


