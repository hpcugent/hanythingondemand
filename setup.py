#!/usr/bin/env python
# -*- coding: latin-1 -*-
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
Setup for Hanything on Demand
"""
import os
import sys
import subprocess
from os.path import join as mkpath
from setuptools import setup, Command

import hod


def setup_openmpi_libpath():
    libpath = os.getenv('LD_LIBRARY_PATH')
    os.environ['LD_LIBRARY_PATH'] = '/usr/lib64/openmpi/lib:%s' % libpath

class BaseCommand(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

class TestCommand(BaseCommand):
    description = "Run unit tests."

    def run(self):
        # Cheeky cheeky LD_LIBRARY_PATH hack for Fedora
        setup_openmpi_libpath()
        ret = subprocess.call(["coverage", "run",  "-m", "pytest", "--cov-config=.coveragerc"])
        sys.exit(ret)

def find_files(*dirs):
    results = []
    for src_dir in dirs:
        for root, dirs, files in os.walk(src_dir):
            results.append((root, map(lambda f: mkpath(root, f), files)))
    return results

PACKAGE = {
    'name': hod.NAME,
    'version': hod.VERSION,
    'author': ['stijn.deweirdt@ugent.be', 'jens.timmerman@ugent.be', 'ewan.higgs@ugent.be'],
    'maintainer': ['stijn.deweirdt@ugent.be', 'jens.timmerman@ugent.be', 'ewan.higgs@ugent.be'],
    'license': "GPL v2",
    'classifiers' : [
        'Programming Language :: Python :: 2'
    ],
    'install_requires': [
        'vsc-base',
        'setuptools',
        # pin mpi4py to 1.3.1 since it's the last of the 1.x series and we don't want to pick up 2.0.0
        # note: mpi4py version is also pinned in tox.ini!
        'mpi4py == 1.3.1',
        'pbs-python',
        'netifaces',
        'netaddr',
    ],
    'tests_require': ['tox', 'pytest', 'pytest-cov', 'coverage', 'mock'],
    'packages': [
        'hod',
        'hod.commands',
        'hod.config',
        'hod.config.autogen',
        'hod.config.writer',
        'hod.node',
        'hod.rmscheduler',
        'hod.subcommands',
        'hod.work',
    ],
    'data_files': find_files('etc'),
    'scripts': ['bin/hod'],
    'cmdclass' : {'test': TestCommand},
    'long_description': open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    'zip_safe': True,
}

if __name__ == '__main__':
    setup(**PACKAGE)
