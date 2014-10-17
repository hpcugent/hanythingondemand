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
@author: Ewan Higgs (Ghent University)
"""

from ConfigParser import NoOptionError, NoSectionError, SafeConfigParser
from collections import Mapping
from copy import deepcopy
from importlib import import_module
from os.path import join as mkpath, dirname, realpath

from hod.config.template import mklocalworkdir

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

def load_service_config(fileobj):
    '''
    Load a .ini style config for a service.
    '''
    config = SafeConfigParser()
    # optionxform = Option Transform; using str stops making it lower case.
    config.optionxform = str
    config.readfp(fileobj)
    return config

def _abspath(filepath, working_dir):
    '''
    Take a filepath and working_dir and return the absolute path for the
    filepath. If the filepath is already absolute then just return it.
    >>> _abspath('somedir/file', '/tmp')
    /tmp/somedir/file
    >>> _abspath('', '/tmp')
    /tmp
    >>> _abspath('/not-tmp/somedir/file', '/tmp')
    /not-tmp/somedir/file
    '''
    if not len(filepath):
        return realpath(working_dir)
    elif filepath[0] == '/': # filepath is already absolute
        return filepath

    return realpath(mkpath(working_dir, filepath))

def _fileobj_dir(fileobj):
    '''
    Return the directory of the fileobj if it exists. If it's a file-like
    object (e.g. StringIO) just return a blank string.
    '''
    if hasattr(fileobj, 'name'):
        return dirname(fileobj.name)
    return ''

def _parse_runs_on(s):
    '''Returns the relevant constant depending on the string argument'''
    options = dict(master=RUNS_ON_MASTER, slave=RUNS_ON_SLAVE, all=RUNS_ON_ALL)
    return options[s.lower()]

def _cfgget(config, section, item, dflt=None):
    '''Get a value from a ConfigParser object or a default if it's not there.'''
    if dflt is None:
        return config.get(section, item)
    try:
        return config.get(section, item)
    except (NoSectionError, NoOptionError):
        return dflt

def parse_comma_delim_list(s):
    '''
    Convert a string containing a comma delimited list into a list of strings
    with no spaces on the end or beginning.
    Blanks are also removed. e.g. 'a,,b' results in ['a', 'b']
    '''
    return [x.strip() for x in filter(lambda x: x.strip(), s.split(','))]

class PreServiceConfigOpts(object):
    r"""
    Manifest file for the group of services responsible for defining service
    level configs which need to be run through the template before any services
    can begin.
    """
    __slots__ = ['version', 'workdir', 'config_writer', 'directories',
            'modules', 'service_configs', 'service_files', 'master_env']

    OPTIONAL_FIELDS=['master_env', 'modules', 'service_configs', 'directories']

    def __init__(self, fileobj):
        _config = load_service_config(fileobj)
        self.version = _cfgget(_config, _META_SECTION, 'version', '')

        self.workdir = _cfgget(_config, _CONFIG_SECTION, 'workdir', '')
        fileobj_dir = _fileobj_dir(fileobj)

        def _fixup_path(cfg):
            return _abspath(cfg, fileobj_dir)

        def _get_list(name):
            return parse_comma_delim_list(_cfgget(_config, _CONFIG_SECTION, name, ''))

        self.modules = _get_list('modules')
        self.master_env = _get_list('master_env')
        self.service_files = _get_list('services')
        self.service_files = [_fixup_path(cfg) for cfg in self.service_files]
        self.directories = _get_list('directories')
        self.config_writer = _cfgget(_config, _CONFIG_SECTION, 'config_writer', '')

        self.service_configs = _collect_configs(_config)

    @property
    def localworkdir(self):
        return mklocalworkdir(self.workdir)

    @property
    def configdir(self):
        return mkpath(self.localworkdir, 'conf')

    def __str__(self):
        return 'PreServiceConfigOpts(version=%s, workdir=%s, modules=%s, ' \
                'master_env=%s, service_files=%s, directories=%s, ' \
                'config_writer=%s, service_configs=%s)' % (self.version,
                        self.workdir, self.modules, self.master_env,
                        self.service_files, self.directories,
                        self.config_writer, self.service_configs)

def preserviceconfigopts_from_file_list(filenames):
    """Create and merge PreServiceConfigOpts from a list of filenames."""
    precfgs = [PreServiceConfigOpts(open(f, 'r')) for f in filenames]
    precfg = reduce(merge, precfgs)
    bad_fields = invalid_fields(precfg)
    if bad_fields:
        raise RuntimeError("A valid configuration could not be generated from the files: %s: missing fields: %s" % (filenames, bad_fields))
    return precfg

def merge(lhs, rhs):
    """
    Merge two objects of the same type based on their __slot__ list. This
    returns a fresh object and the originals should not be replaced.
    Rules:
        List types are concatenated.
        Dict types are merged using a deep merge.
        String types are overwritten. 
    """
    if type(lhs) != type(rhs):
        raise RuntimeError('merge can only use two of the same type')

    def _update(a, b):
        for k, v in b.iteritems():
            if isinstance(v, Mapping):
                c = _update(a.get(k, dict()), v)
                a[k] = c
            else:
                a[k] = b[k]
        return a

    lhs = deepcopy(lhs)
    for attr in lhs.__slots__:
        _lhs = getattr(lhs, attr)
        _rhs = getattr(rhs, attr)
        # cat lists
        if isinstance(_lhs, list):
            _lhs += _rhs
        # update dicts
        elif isinstance(_lhs, Mapping):
            _lhs = _update(_lhs, _rhs)
        # replace strings
        elif isinstance(_lhs, basestring) and _rhs:
            _lhs = _rhs

    return lhs

def invalid_fields(obj):
    """Return list of fields which are empty."""
    bad_fields = []
    for attr in obj.__slots__:
        if attr not in obj.OPTIONAL_FIELDS and not getattr(obj, attr):
            bad_fields.append(attr)
    return bad_fields

def _collect_configs(config):
    """Convert sections into dicts of options"""
    service_configs = dict()
    for section in [s for s in config.sections() if s not in [_META_SECTION, _CONFIG_SECTION]]:
        option_dict = dict()
        options = config.options(section)
        for option in options:
            option_dict[option] = config.get(section, option)

        service_configs[section] = option_dict

    return service_configs

def env2str(env):
    '''
    Take a dict of environment variable names mapped to their values and
    convert it to a string that can be used to prepend a command.
    '''
    envstr = ''
    for k, v in sorted(env.items()):
        envstr += '%s="%s" ' % (k, v)
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
        return mklocalworkdir(self._tr.workdir)

    @property
    def configdir(self):
        return mkpath(self.localworkdir, 'conf')

    @property
    def env(self):
        return dict([(k, self._tr(v)) for k, v in self._config.items(_ENVIRONMENT_SECTION)])

    def __str__(self):
        return 'ConfigOpts(name=%s, runs_on=%d, pre_start_script=%s, ' \
                'start_script=%s, stop_script=%s, workdir=%s, localworkdir=%s)' %  (self.name,
                self._runs_on, self.pre_start_script, self.start_script,
                self.stop_script, self.workdir, self.localworkdir)

    def __repr__(self):
        return 'ConfigOpts(name=%s, runs_on=%d)' % (self.name, self._runs_on)

    def __getstate__(self): 
        return self.__dict__

    def __setstate__(self, d): 
        self.__dict__.update(d)

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
        f.write(config_writer(outfile, data_dict, template_resolver))
