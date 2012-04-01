"""
Add some types 
"""

import os, stat

class HostnamePort:
    """This is an hostname with port"""
    def __init__(self, txt=None):
        self.hostname = None
        self.port = None
        if type(txt) == str:
            txt = txt.split(':')
        if type(txt) in (list, tuple,):
            self.hostname = txt[0] or None ## ':10' is hostname None and port 10
            if len(txt) > 1: ## and nothing else matters....
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
    def __str__(self):
        hnp = HostnamePort.__str__(self)
        return "hdfs://%s/" % hnp

class KindOfList:
    def __init__(self, kol=None):
        self.kindoflist = []
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

class Directories(KindOfList):
    """Directories"""
    def __init__(self, dirs=None):
        KindOfList.__init__(self, dirs)
        self.perms = stat.S_IRWXU

    def __str__(self):
        """Hadoop expects mulitple directoris in comma-separated list"""
        ds = self.kindoflist
        if ds is None:
            ds = []
        return ','.join(["%s" % d for d in ds]) ## deal with None as element in list


    def check(self):
        """Check if directories exist, if not create them with proper permissions"""
        for d in self.kindoflist:
            if not os.path.isdir(d):
                os.makedirs(d, self.perms)
            os.chmod(d, self.perms)

class Arguments(KindOfList):
    """Arguments (space separated)"""
    def __str__(self):
        d = self.kindoflist
        if d is None:
            d = []
        return ' '.join(d)
