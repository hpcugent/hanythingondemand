##
# Copyright 2009-2015 Ghent University
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
IPython Notebook autoconfiguration.

@author: Ewan Higgs (Ghent University)
"""

import string

def ipython_notebook_config(workdir, _):
    '''
    Generate config 
    '''
    template = r"""
c = get_config()

# Kernel config
c.IPKernelApp.pylab = 'inline'  # if you want plotting support always

# Notebook config
c.NotebookApp.open_browser = False
c.NotebookApp.password = u'sha1:{hashed_password}'
# It is a good idea to put it on a known, fixed port
c.NotebookApp.port = 8888
c.NotebookApp.ipython_dir = u'{workdir}'
c.NotebookApp.notebook_dir = u'{workdir}'
"""
    template = string.Template(template)
    # IPython.lib.passwd('hanythingondemand')
    # 'sha1:906f33be372a:2c33c548645189cfa7a37ea0b77ccfb65852ba28'
    passwd_hash = '906f33be372a:2c33c548645189cfa7a37ea0b77ccfb65852ba28'
    file_contents = template.substitute(hashed_password=passwd_hash, workdir=workdir)
    return file_contents

def autogen_config(workdir, node_info):
    '''
    Bless an ipython notebook config with automatically generated information
    based on the nodes.

    NB: The name is important here; it must be 'autogen_config' as it's loaded
    lazily from hod.config.config.
    '''
    cfg2fn = {
        'ipython_notebook.config.py': ipython_notebook_config,
    }
    config_dict = dict()
    for cfg, fn in cfg2fn.items():
        dflts = fn(workdir, node_info)
        config_dict[cfg] = dflts
    return config_dict
