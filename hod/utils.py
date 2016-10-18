#!/usr/bin/env python
# ##
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
"""
Utility functions for hanythingondemand

@author: Kenneth Hoste (Universiteit Gent)
"""

import os

def only_if_module_is_available(modname):
    """Decorator to guard functions/methods against missing required module with specified name."""
    def wrap(orig):
        """Decorated function, raises ImportError if specified module is not available."""
        try:
            __import__(modname)
            return orig

        except ImportError as err:
            def error(*args):
                raise ImportError("%s; required module '%s' is not available" % (err, modname))
            return error

    return wrap

def setup_diagnostic_environment():
    """
    When we run diagnostic functions (e.g. genconfig, help-template), we need to
    pretend we are in a job so we poke some values into the environment.
    """
    if 'PBS_DEFAULT' not in os.environ:
        os.environ['PBS_DEFAULT'] = 'pbs-master'
    os.environ['PBS_JOBID'] = '123.%s' % os.environ['PBS_DEFAULT']


