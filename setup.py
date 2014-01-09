#!/usr/bin/env python
# -*- coding: latin-1 -*-
##
# Copyright 2009-2012 Ghent University
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
Setup for Hanything on Demand

@author: Andy Georges
@author: Stijn De Weirdt
@author: Wouter Depypere
@author: Kenneth Hoste
@author: Jens Timmerman
"""

import os
from setuptools import setup

PACKAGE = {
    'name': 'hod',
    'version': '2.1.1',
    'author': 'Stijn De Weirdt',
    'maintainer': 'Jens Timmerman',
    'license': "GPL v2",
    'package_dir': {'': 'lib', 'tests': ''},
    'install_requires': [
        'vsc-base >= 1.7.2',
        'vsc-mympirun >= 3.2.2',
    ],
    'packages': [
        'tests',
        'hod',
        'hod.work',
        'hod.commands',
        'hod.config',
        'hod.rmscheduler',
    ],
    'scripts': ['bin/hod_main.py', 'bin/hod_pbs.py'],
    'url': 'https://github.ugent.be/hpcugent/hanythingondemand',
    'download_url': 'https://github.ugent.be/hpcugent/hanythingondemand',
    'long_description': open(os.path.join(os.path.dirname(__file__), 'README')).read(),
}

setup(**PACKAGE)
