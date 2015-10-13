#!/usr/bin/env python
# #
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
# #
"""
Tests for utility functions for printing text in tables.

@author: Ewan Higgs (Universiteit Gent)
"""

import unittest

import hod.table as ht

class TestTables(unittest.TestCase):
    def test_format_table_no_headers(self):
        expect = "1\t2\t3\n"
        expect += "4\t5\t6\n"
        expect += "7\t8\t9"

        contents = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        self.assertEqual(expect, ht.format_table(contents, None))

    def test_format_table_headers(self):
        expect = "Header1\tHeader2\tHeader3\n"
        expect += "1      \t2      \t3      \n"
        expect += "4      \t5      \t6      \n"
        expect += "7      \t8      \t9      "

        contents = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        headers = ['Header1', 'Header2', 'Header3']
        self.assertEqual(expect, ht.format_table(contents, headers))

    def test_format_tablecontent_longer_than_header(self):
        expect = "H1     \tH2     \tH3     \n"
        expect += "Col1   \tCol2   \tCol3   \n"
        expect += "Column1\tColumn2\tColumn3"

        contents = [['Col1', 'Col2', 'Col3'], ['Column1', 'Column2', 'Column3']]
        headers = ['H1', 'H2', 'H3']
        self.assertEqual(expect, ht.format_table(contents, headers))


    def test_format_table_bad_header_length(self):
        contents = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        headers = ['Header1', 'Header2']
        self.assertRaises(ValueError, ht.format_table, contents, headers)

