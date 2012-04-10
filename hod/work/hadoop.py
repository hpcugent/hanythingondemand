from hod.work.work import Work
from hod.config.hadoopopts import HadoopOpts
from hod.config.customtypes import Arguments


import os, pwd, re

from vsc import fancylogger
fancylogger.setLogLevelDebug()


class Hadoop(Work, HadoopOpts):
    """Base Hadoop work class"""
    def __init__(self, ranks, shared):
        Work.__init__(self, ranks)
        HadoopOpts.__init__(self, shared)

    def interface_to_nn(self):
        """What interface can reach the namenode"""
        nn = self.params.get('fs.default.name', self.default_fsdefault)
        if None in nn:
            self.log.error("No namenode set")
            return None

        intf = self.thisnode.ip_interface_to(nn.hostname)
        if intf:
            self.log.debug("namenode can be reached by intf %s" % intf)
            return intf
        else:
            self.log.error("namenode %s cannot be reached by any of the local interfaces %s" % (nn, self.thisnode.network))

    def prepare_extra_work_cfg(self):
        """Add some custom parameters"""

    def prepare_work_cfg(self):
        """prepare the config: collect the parameters and make the necessary xml cfg files"""
        self.basic_cfg()
        if self.basedir is None:
            self.basedir = os.path.join('/tmp', 'hod', pwd.getpwuid(os.getuid())[0], "%d" % self.rank, self.name)

        self.prepare_extra_work_cfg()

        if None in self.default_fsdefault:
            self.log.error("Primary nameserver still not set.")

        ## set the defaults
        self.make_opts_env_defaults()


        self.use_sdp(False)

        ## make the cfg
        self.make_opts_env_cfg()

        ## set the controldir to the confdir
        self.controldir = self.confdir

    def use_sdp(self, allowsdp=True):
        """When IB is being used, set jdk SDP support"""
        if not allowsdp:
            self.log.debug("Ignoring SDP")
            return

        intf = self.interface_to_nn()
        ib_regexp = re.compile(r"^(ib)\d+")
        if not ib_regexp.search(intf[2]):
            self.log.debug("Interface to namenode is not IB %s" % (intf))
            return
        else:
            self.log.debug("Interface to namenode is IB %s" % (intf))

        if self.javaversion['major'] < 1 or self.javaversion['minor'] < 7:
            self.log.warn("Java SDP support requires at least JDK 1.7")
            return

        netw = "%s/%s" % (intf[1], intf[3])
        sdpconf = "connect %s *\nbind %s *\n" % (netw, netw)
        sdpconf_fn = os.path.join(self.confdir, 'sdp.conf')
        fh = open(sdpconf_fn, 'w')
        fh.write(sdpconf)
        fh.close()
        self.log.debug("Written sdp.conf %s with content %s" % (sdpconf_fn, sdpconf))

        javaopts = Arguments(['-Dcom.sun.sdp.conf=%s' % sdpconf_fn, '-Djava.net.preferIPv4Stack=true'])
        sdpdebug = True
        if sdpdebug:
            debuglog = os.path.join("%s" % self.env_params['HADOOP_LOG_DIR'], "sdp.debug.log")
            self.log.debug("Going to log sdp to %s" % debuglog)
            javaopts += Arguments(["-Dcom.sun.sdp.debug=%s" % debuglog])

        self.add_param('mapred.child.java.opts', javaopts)
        self.add_param('HADOOP_OPTS', javaopts, is_env=True)

