##
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
##
"""
Add some types

@author: Stijn De Weirdt
"""

import os
import stat


class HostnamePort:

    """This is an hostname with port"""
    def __init__(self, txt=None):
        self.hostname = None
        self.port = None
        if type(txt) == str:
            txt = txt.split(':')
        if type(txt) in (list, tuple,):
            self.hostname = txt[0] or None  # ':10' is hostname None and port 10
            if len(txt) > 1:  # and nothing else matters....
                self.port = txt[1]

    def __str__(self):
        hn = self.hostname
        if hn is None:
            hn = '0.0.0.0'
        p = self.port
        if p is None:
            p = 0
        return "%s:%s" % (hn, p)

    def __contains__(self, d):
        return d == self.hostname or d == "%s" % self


class HdfsFs(HostnamePort):
    def __init__(self, txt=None, path='/'):
        HostnamePort.__init__(self, txt)
        self.fspath = path

    def __str__(self):
        hnp = HostnamePort.__str__(self)
        return "hdfs://%s%s" % (hnp, self.fspath)


class KindOfList:
    def __init__(self, kol=None):
        self.kindoflist = []
        self.str_sepa = ','  # default comma-separated
        if type(kol) in (str,) or kol is None:
            kol = [kol]

        if type(kol) in (list, tuple,):
            self.kindoflist = list(kol)
        else:
            raise Exception("Unknown kindoflist type %s %s" % (type(kol), kol))

    def append(self, d):
        self.kindoflist.append(d)

    def __contains__(self, d):
        return d in self.kindoflist

    def __iter__(self):
        return self.kindoflist.__iter__()

    def __add__(self, y):
        ## strip None first
        no_nones = [x for x in self.kindoflist if not x is None]
        if hasattr(y, 'kindoflist'):
            self.kindoflist = no_nones + y.kindoflist
        else:
            self.kindoflist = no_nones + y

    def __iadd__(self, y):
        self.__add__(y)
        return self

    def __str__(self):
        d = self.kindoflist
        if d is None:
            d = []
        return self.str_sepa.join(["%s" % x for x in d if not x is None])


class Servers(KindOfList):
    """Comma separated list of servers"""


class UserGroup:
    def __init__(self, users=None, groups=None):
        self.users = KindOfList(users)
        self.groups = KindOfList(groups)

    def add_users(self, users):
        """Add users"""
        if type(users) in (str,):
            users = [users]
        self.users += users

    def add_groups(self, groups):
        if type(groups) in (str,):
            groups = [groups]
        self.groups += groups

    def __str__(self):
        """space separated list of comma-separated list of users and groups"""
        txt = []
        users_txt = "%s" % self.users
        grp_txt = "%s" % self.users
        if len(users_txt) > 0:
            txt.append(users_txt)
        if len(grp_txt) > 0:
            txt.append(grp_txt)
        return ' '.join(txt)

    def __contains__(self, d):
        ## OR logic
        return (d in self.users) or (d in self.groups)


class Directories(KindOfList):
    """Directories"""
    def __init__(self, dirs=None):
        KindOfList.__init__(self, dirs)
        self.perms = stat.S_IRWXU

    def check(self):
        """Check if directories exist, if not create them with proper permissions"""
        for d in self.kindoflist:
            if not os.path.isdir(d):
                os.makedirs(d, self.perms)
            os.chmod(d, self.perms)


class Arguments(KindOfList):
    """Arguments (space separated)"""
    def __init__(self, args=None):
        KindOfList.__init__(self, args)
        self.str_sepa = ' '


class Params(dict):
    """dict with improved __str__"""
    def __str__(self):
        tmp = {}
        for k, v in self.items():
            tmp[k] = "%s" % v
        return "%s" % tmp


class ParamsDescr(dict):
    """dict with improved __str__"""
    def __str__(self):
        tmp = {}
        for k, v in self.items():
            if type(v) in (list, tuple,):
                tmp[k] = ["%s" % x for x in v]
            else:
                tmp[k] = "%s" % str(v)
        return "%s" % tmp


class Boolean:
    """bool class with slightly different __str__"""
    def __init__(self, val=None):
        if val:
            self.value = True
        elif val is None:
            self.value = None
        else:
            self.value = False

    def __contains__(self, d):
        return d == self.value

    def __str__(self):
        txt = "%s" % self.value
        return txt.lower()
