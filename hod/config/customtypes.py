"""
Add some types 
"""

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

class Directories:
    """Directories"""
    def __init__(self, dirs=None):
        self.kindoflist = []
        if type(dirs) in (str,) or dirs is None:
            dirs = [dirs]
        if type(dirs) in (list, tuple,):
            self.kindoflist = list(dirs)
        elif type(dirs) in (Directories,):
            self.kindoflist = dirs.kindoflist

    def __str__(self):
        """Hadoop expects mulitple directoris in comma-separated list"""
        ds = self.kindoflist
        if ds is None:
            ds = []
        return ','.join(["%s" % d for d in ds]) ## deal with None as element in list

    def append(self, d):
        self.kindoflist.append(d)

    def __contains__(self, d):
        return d in self.kindoflist

    def __iter__(self):
        return self.kindoflist.__iter__()

class Arguments(Directories):
    """Arguments (space separated)"""
    def __str__(self):
        d = self.kindoflist
        if d is None:
            d = []
        return ' '.join(d)
