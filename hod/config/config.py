# #
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
# #
"""
@author: Ewan Higgs (Ghent University)
"""

import os

from ConfigParser import NoOptionError, NoSectionError, SafeConfigParser
from collections import Mapping, namedtuple
from copy import deepcopy
from os.path import join as mkpath, dirname, realpath
from pkg_resources import Requirement, resource_filename, resource_listdir

import hod
from hod.node.node import Node
from hod.commands.command import COMMAND_TIMEOUT
import hod.config.template as hct


from vsc.utils import fancylogger
_log = fancylogger.getLogger(fname=False)

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

HOD_ETC_DIR = os.path.join('etc', 'hod')


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


def _cfgget(config, section, item, dflt=None, **kwargs):
    '''
    Get a value from a ConfigParser object or a default if it's not there.
    Options in kwargs override the config.
    '''
    if kwargs.get(item, None) is not None:
        return kwargs[item]
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
    return [tok.strip() for tok in [el for el in s.split(',') if el.strip()]]


class PreServiceConfigOpts(object):
    r"""
    Manifest file for the group of services responsible for defining service
    level configs which need to be run through the template before any services
    can begin.

    aka hod.conf or hodconf.
    """
    __slots__ = ['version', 'workdir', 'config_writer', 'directories',
                 'autogen', 'modulepaths', 'modules', 'service_configs', 'service_files',
                 'master_env', '_hodconfdir'
                ]

    OPTIONAL_FIELDS = ['master_env', 'modulepaths', 'modules', 'service_configs', 'directories', 'autogen']

    @staticmethod
    def from_file_list(filenames, **kwargs):
        """Create and merge PreServiceConfigOpts from a list of filenames."""
        precfgs = [PreServiceConfigOpts(open(f, 'r'), **kwargs) for f in filenames]
        precfg = reduce(merge, precfgs)
        bad_fields = invalid_fields(precfg)
        if bad_fields:
            raise RuntimeError("A valid configuration could not be generated from the files: %s: missing fields: %s" %
                               (filenames, bad_fields))
        return precfg

    def __init__(self, fileobj, **kwargs):
        _config = load_service_config(fileobj)
        self.version = _cfgget(_config, _META_SECTION, 'version', '', **kwargs)

        self.workdir = _cfgget(_config, _CONFIG_SECTION, 'workdir', '', **kwargs)
        self._hodconfdir = _fileobj_dir(fileobj)

        def _fixup_path(cfg):
            return _abspath(cfg, self._hodconfdir)

        def _get_list(name):
            '''
            With lists, we don't want to overwrite the value with kwargs.
            Mergely append.
            '''
            lst = parse_comma_delim_list(_cfgget(_config, _CONFIG_SECTION, name, ''))
            if kwargs.get(name, None) is not None:
                lst.extend(parse_comma_delim_list(kwargs[name]))
            return lst

        self.modulepaths = _get_list('modulepaths')
        self.modules = _get_list('modules')
        self.master_env = _get_list('master_env')
        self.service_files = _get_list('services')
        self.service_files = [_fixup_path(cfg) for cfg in self.service_files]
        self.directories = _get_list('directories')
        self.config_writer = _cfgget(_config, _CONFIG_SECTION, 'config_writer', '')

        self.service_configs = _collect_configs(_config)
        self.autogen = parse_comma_delim_list(_cfgget(_config, _CONFIG_SECTION, 'autogen', ''))

    @property
    def localworkdir(self):
        return hct.mklocalworkdir(self.workdir)

    @property
    def configdir(self):
        return mkpath(self.localworkdir, 'conf')

    @property
    def hodconfdir(self):
        return self._hodconfdir

    def autogen_configs(self):
        '''
        Lazily generate the missing configurations as a convenience to
        users.
        This should only be run when processing the config file while the job is
        being run (e.g. from hod.subcommands.local.LocalApplication). e.g. If
        workdir is a directory on a file system that is not accessible from the
        login node then we can't process this information from the login node.
        '''
        node = Node()
        node_info = node.go()
        _log.debug('Collected Node information: %s', node_info)
        for autocfg in self.autogen:
            fn = autogen_fn(autocfg)
            new_configs = fn(self.workdir, node_info)
            for cfgname in new_configs.keys():
                if cfgname in self.service_configs:
                    new_configs[cfgname].update(self.service_configs[cfgname])
            self.service_configs = new_configs

    def __str__(self):
        return 'PreServiceConfigOpts(version=%s, workdir=%s, modulepaths=%s, modules=%s, ' \
                'master_env=%s, service_files=%s, directories=%s, ' \
                'config_writer=%s, service_configs=%s)' % (self.version,
                        self.workdir, self.modulepaths, self.modules, self.master_env,
                        self.service_files, self.directories,
                        self.config_writer, self.service_configs)


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
        if not (attr in obj.OPTIONAL_FIELDS or getattr(obj, attr) or
                attr.startswith('_')):
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

    @staticmethod
    def from_file(fileobj, template_resolver):
        """Load a ConfigOpts from a configuration file."""
        config = load_service_config(fileobj)

        name = _cfgget(config, _UNIT_SECTION, 'Name')
        runs_on = _parse_runs_on(_cfgget(config, _UNIT_SECTION, 'RunsOn'))
        pre_start_script = _cfgget(config, _SERVICE_SECTION, 'ExecStartPre', '')
        start_script = _cfgget(config, _SERVICE_SECTION, 'ExecStart')
        stop_script = _cfgget(config, _SERVICE_SECTION, 'ExecStop')
        env = dict(config.items(_ENVIRONMENT_SECTION))

        return ConfigOpts(name, runs_on, pre_start_script, start_script, stop_script, env, template_resolver)

    def to_params(self, workdir, modulepaths, modules, master_template_args):
        """Create a ConfigOptsParams object from the ConfigOpts instance"""
        return ConfigOptsParams(self.name, self._runs_on, self._pre_start_script, self._start_script,
                                self._stop_script, self._env, workdir, modulepaths, modules,
                                master_template_args, self.timeout)

    @staticmethod
    def from_params(params, template_resolver):
        """Create a ConfigOpts instance from a ConfigOptsParams instance"""
        return ConfigOpts(params.name, params.runs_on, params.pre_start_script, params.start_script,
                          params.stop_script, params.env, template_resolver, params.timeout)

    def __init__(self, name, runs_on, pre_start_script, start_script, stop_script, env, template_resolver, 
                    timeout=COMMAND_TIMEOUT):
        self.name = name
        self._runs_on = runs_on
        self._tr = template_resolver
        self._pre_start_script = pre_start_script
        self._start_script = start_script
        self._stop_script = stop_script
        self._env = env
        self.timeout = timeout

    @property
    def pre_start_script(self):
        return self._tr(self._pre_start_script)

    @property
    def start_script(self):
        return self._tr(self._start_script)

    @property
    def stop_script(self):
        return self._tr(self._stop_script)

    @property
    def workdir(self):
        return self._tr.workdir

    @property
    def localworkdir(self):
        return hct.mklocalworkdir(self._tr.workdir)

    @property
    def configdir(self):
        return mkpath(self.localworkdir, 'conf')

    @property
    def env(self):
        return dict([(k, self._tr(v)) for k, v in self._env.items()])

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
            raise ValueError('ConfigOpts.runs_on has invalid value: %s' % self._runs_on)

# Parameters to send over the network to allow slaves to construct hod.config.ConfigOpts
# objects
ConfigOptsParams = namedtuple('ConfigOptsParams', [
    'name',
    'runs_on',
    'pre_start_script',
    'start_script',
    'stop_script',
    'env',
    'workdir',
    'modulepaths',
    'modules',
    'master_template_kwargs',
    'timeout',
])

def autogen_fn(name):
    """
    Given a product name (hadoop, hdfs, etc), generate default configuration
    parameters for things that haven't been defined yet.

    Params
    ------
    name : `str`
    Product name.

    Returns
    -------
    Function taking a working directory (for detecting block sizes and so on)
    and a dict of config settings.
    """
    module = __import__('hod.config.autogen.%s' % name, fromlist=['hod.config.autogen'])
    return getattr(module, 'autogen_config')


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
    module_name = '.'.join(policy_path_list[:-1])
    parent_pkg = '.'.join(policy_path_list[:-2])
    fn = policy_path_list[-1]
    try:
        module = __import__(module_name, fromlist=[parent_pkg])
    except ImportError as err:
        _log.error('Could not import module "%s" from "%s": %s', module_name, parent_pkg, err)
        raise
    return getattr(module, fn)


def write_service_config(outfile, data_dict, config_writer, template_resolver):
    """Write service config files to disk."""
    with open(outfile, 'w') as f:
        f.write(config_writer(outfile, data_dict, template_resolver))


def resolve_dists_dir():
    """Resolve path to distributions."""
    pkg = Requirement.parse(hod.NAME)
    return resource_filename(pkg, HOD_ETC_DIR)


def resolve_dist_path(dist):
    """
    Given a distribution name like Hadoop-2.3.0-cdh5.0.0, return the path to the
    relevant hod.conf
    """
    distpath = resolve_dists_dir()
    distpath = mkpath(distpath, dist, 'hod.conf')
    return distpath


def avail_dists():
    """Return a list of available distributions"""
    pkg = Requirement.parse(hod.NAME)
    return sorted(resource_listdir(pkg, HOD_ETC_DIR))


def resolve_config_paths(config, dist):
    """
    Take two strings and return:
    1. config if it's defined.
    2. The expanded dist path if config is not defined.
    """
    if config:
        if os.path.exists(config):
            path = config
        else:
            raise ValueError("Specified config file '%s' does not exist." % config)
    elif dist:
        path = resolve_dist_path(dist)
        if not os.path.exists(path):
            raise ValueError("Config file for specified dist '%s' does not exist: %s" % (dist, path))
    else:
        raise RuntimeError('A config or a dist must be provided')

    return path

def load_hod_config(filenames, workdir, modulepaths, modules):
    '''
    Load the manifest config (hod.conf) files.
    '''
    m_config_filenames = parse_comma_delim_list(filenames)
    _log.info('Loading "%s" manifest config', m_config_filenames)
    m_config = PreServiceConfigOpts.from_file_list(m_config_filenames, workdir=workdir,
                                                   modulepaths=modulepaths, modules=modules)
    _log.debug('Loaded manifest config: %s', str(m_config))
    return m_config
