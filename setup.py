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
from os.path import join as mkpath
import sys
import subprocess
from setuptools import setup, Command

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
        ret = subprocess.call("python -m unittest discover -b -s test/unit -v".split(' '))
        sys.exit(ret)

class CoverageCommand(BaseCommand):
    description = "Run unit tests."

    def run(self):
        setup_openmpi_libpath()
        ret = subprocess.call(["coverage", "run", "--omit", "*/.virtualenvs/*", 
            "-m", "unittest", "discover", "-v", "-b", "-s", "test/unit/"])
        if not ret:
            ret = subprocess.call(["coverage", "report"])
        sys.exit(ret)


def find_files(*dirs):
    results = []
    for src_dir in dirs:
        for root, dirs, files in os.walk(src_dir):
            results.append((root, map(lambda f: mkpath(root, f), files)))
    return results

PACKAGE = {
    'name': 'hanythingondemand',
    'version': '2.3.0',
    'author': ['stijn.deweirdt@ugent.be', 'jens.timmerman@ugent.be', 'ewan.higgs@ugent.be'],
    'maintainer': ['stijn.deweirdt@ugent.be', 'jens.timmerman@ugent.be', 'ewan.higgs@ugent.be'],
    'license': "GPL v2",
    'install_requires': [
        'vsc-base >= 1.7.3',
        'mpi4py',
        'pbs-python',
        'netifaces',
        'netaddr',
    ],
    'tests_require': ['tox', 'pytest', 'coverage', 'mock'],
    'packages': [
        'hod',
        'hod.applications',
        'hod.commands',
        'hod.config',
        'hod.config.autogen',
        'hod.config.writer',
        'hod.node',
        'hod.rmscheduler',
        'hod.work',
    ],
    'data_files': find_files('etc'),
    'scripts': ['bin/hod', 'bin/hod-local'],
    'cmdclass' : {'test': TestCommand, 'cov': CoverageCommand},
    'long_description': open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
}

if __name__ == '__main__':
    setup(**PACKAGE)
