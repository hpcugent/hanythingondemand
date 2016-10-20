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

from collections import namedtuple
from os.path import join as mkpath

import os
import pwd
import socket
import string

import hod.node.node as node

from vsc.utils import fancylogger
_log = fancylogger.getLogger(fname=False)

ConfigTemplate = namedtuple('ConfigTemplate', 'name, fn, doc')

def _config_template_error(name):
    '''Placeholder function for config templates for when we don't have access
    to the master node fields yet.'''
    def _fn():
        msg = 'Field "%s" not yet available' % name
        _log.error(msg)
    return _fn

def _config_template_stub(name, doc):
    ct = ConfigTemplate(name, _config_template_error(name), doc)
    return ct

class TemplateRegistry(object):
    '''
    Lookup object for template configuration parameters.
    '''
    def __init__(self):
        self.fields = dict()

    def register(self, template_config):
        '''Register a ConfigTemplate.'''
        self.fields[template_config.name] = template_config

    def to_kwargs(self):
        '''Convert TemplateRegistry to keyword args dict.'''
        kwargs = {}
        for k, v in self.fields.items():
            kwargs[k] = v.fn() if callable(v.fn) else v.fn
        return kwargs


def register_templates(template_registry, config_opts):
    '''
    Register the common templates.
    Params
    ------
    template_registry : `TemplateRegistry`
        Registry to update.

    config_opts : `hod.mpiservice.ConfigOptsParams`
        Configuration structure holding our config options.
    '''
    workdir = config_opts.workdir
    modules = config_opts.modules
    local_data_network = node.sorted_network(node.get_networks())[0]
    templates = [
        _config_template_stub('masterhostname', 'Hostname bound to the Fully Qualified Domain Name (FQDN) of the master node.'),
        _config_template_stub('masterhostaddress', 'Address bound to the Fully Qualified Domain Name (FQDN) of the master node.'),
        _config_template_stub('masterdataname', 'Hostname bound to the Infiniband adaptor on the master node if available'),
        _config_template_stub('masterdataaddress', 'Address bound to the Infiniband adaptor on the master node if available'),
        ConfigTemplate('hostname', socket.getfqdn, 'Fully Qualified Domain Name (FQDN)'),
        ConfigTemplate('hostaddress', lambda: socket.gethostbyname(socket.getfqdn()), 'IP address registered as the FQDN'),
        ConfigTemplate('dataname', local_data_network.hostname, 'Infiniband hostname if available'),
        ConfigTemplate('dataaddress', local_data_network.addr, 'Infiniband address if available'),
        ConfigTemplate('workdir', workdir, 'Base directory for configuration and logging, e.g. /tmp, or somewhere on a shared file system.'),
        ConfigTemplate('localworkdir', lambda: mklocalworkdir(workdir), 'Subdirectory of workdir with user, host, and pid in the name to make it distinct from other workdirs for use on shared file systems'),
        ConfigTemplate('user', _current_user, 'Current user'),
        ConfigTemplate('pid', os.getpid, 'PID for the current process'),
        ConfigTemplate('modules', lambda: ' '.join(modules), 'Modules listed in the hod.conf'),
        ]

    for ct in templates:
        template_registry.register(ct)

def mklocalworkdir(workdir):
    '''
    Construct the pathname for a workdir with a path local to this
    host/job/user.
    '''
    user = _current_user()
    pid = os.getpid()
    jobid = os.getenv('PBS_JOBID')
    if jobid is None:
        raise RuntimeError('$PBS_JOBID must be defined to create a localworkdir.')
    hostname = socket.getfqdn()
    dir_name = '.'.join([user, hostname, str(pid)])
    return mkpath(workdir, 'hod', jobid, dir_name)

def _current_user():
    '''
    Return the current user name as recommended by documentation of
    os.getusername.
    '''
    return pwd.getpwuid(os.getuid()).pw_name

def resolve_config_str(tmpl_str, **template_kwargs):
    '''
    Given a string, resolve the templates based on template_dict and
    template_kwargs.

    If a non string is provided, the original value is returned.
    '''
    if not isinstance(tmpl_str, basestring):
        return tmpl_str
    template = string.Template(tmpl_str)
    try:
        retval = template.substitute(template_kwargs)
    except TypeError as err:
        raise TypeError('Error processing "%s": %s' % (tmpl_str, err))
    return retval

class TemplateResolver(object):
    '''
    Resolver for templates. This is partially applied wrapper around
    resolve_config_str but picklable.
    '''
    def __init__(self, **template_kwargs):
        self.workdir = template_kwargs['workdir'] # raise if not found...
        self._template_kwargs = template_kwargs
        self._template_kwargs.update(os.environ)

    def __call__(self, tmpl_str):
        '''Given a string with template placeholders, return the resolved string'''
        return resolve_config_str(tmpl_str, **self._template_kwargs)
