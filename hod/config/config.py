from ConfigParser import SafeConfigParser
import socket
import string
from collections import namedtuple, OrderedDict
import subprocess
import os
import pwd
from os.path import join as mkpath, realpath, dirname
from functools import partial
import logging as log

_EXEC_SECTION = 'Exec'
_ENVIRONMENT_SECTION = 'Environment'
_CONFIG_SECTION = 'Config'

def _templated_strings():
    '''Return the template dict with the name fed through.'''
    basedir = _mkhodbasedir()

    _strings = {
        'hostname': socket.getfqdn,
        'basedir': lambda: basedir,
        'configdir': lambda: mkpath(basedir, 'conf'),
        'workdir': lambda:  mkpath(basedir, 'work'),
        'user': _current_user,
        'pid': os.getpid,
        'pbsjobid': lambda: os.getenv('PBS_JOBID'),
        'pbsjobname': lambda: os.getenv('PBS_JOBNAME'),
        'pbsnodefile': lambda: os.getenv('PBS_NODEFILE'),
        }

    return _strings

def load_service_config(fileobj):
    '''
    Load a .ini style config for a service.
    '''
    config = SafeConfigParser()
    # stop ConfigParser from making everything lower case.
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

def resolve_config_str(s):
    template = string.Template(s)
    template_strings = _templated_strings()
    resolved_templates = _resolve_templates(template_strings)
    return template.substitute(**resolved_templates)


def _configs(conf_dir):
    '''Find all the configs in the config_directory'''
    results = []
    for root, dirs, files in os.walk(conf_dir):
        results.append((root, map(lambda f: mkpath(root, f), files)))
    return results

def _basedir():
    return os.getenv('TMPDIR', '/tmp')

def _current_user():
    return pwd.getpwuid(os.getuid())[0]

def _mkhodbasedir():
    user = _current_user()
    pid = os.getpid()
    hostname = socket.getfqdn()
    dir_name = ".".join([user, hostname, str(pid)])
    return mkpath(_basedir(), 'hod', dir_name)

def mkpathabs(filepath, working_dir):
    '''
    Take a filepath and working_dir and return the absolute path for the
    filepath. If the filepath is already absolute then just return it.
    '''
    if filepath[0] == '/': # filepath is already absolute
        return filepath

    return realpath(mkpath(working_dir, filepath))
    
def _fileobj_dir(fileobj):
    if hasattr(fileobj, 'name'):
        return dirname(fileobj.name)
    return ''
    
class ConfigOpts(object):
    r"""
    Wrapper for the service configuration.
    Each of the config values can have a $variable which will be replaces
    by the value in the template strings except 'name'. Name cannot be
    templated.
    """

    def __init__(self, fileobj):
        self._config = load_service_config(fileobj)
        self.name = self._config.get(_EXEC_SECTION, 'name')

        _r = partial(resolve_config_str)
        self.name = _r(self._config.get(_EXEC_SECTION, 'name'))
        self.start_script = _r(self._config.get(_EXEC_SECTION, 'start-script'))
        self.stop_script = _r(self._config.get(_EXEC_SECTION, 'stop-script'))

        self.env = OrderedDict([(k, _r(v)) for k, v in self._config.items(_ENVIRONMENT_SECTION)])
        config_config = self._config.items('Config')

        self.config_file = _r(self._config.get(_CONFIG_SECTION, 'config-file'))
        if len(self.config_file):
            self.config_file = mkpathabs(self.config_file, _fileobj_dir(fileobj))

        self.basedir = _mkhodbasedir()
        self.configdir = mkpath(self.basedir, 'conf')

    def setenv(self):
        for k,v in self.env.items():
            os.environ[k] = v
