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

@author: Stijn De Weirdt
"""
import os
import pwd
import tempfile
import re

from hod.work.work import Work
from hod.config.hadoopopts import HadoopOpts
from hod.config.customtypes import Arguments


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
            self.basedir = tempfile.mkdtemp(prefix='hod', suffix=".".join(
                pwd.getpwuid(os.getuid())[0],  # current user uid
                "%d" % self.rank,
                self.name
            ))

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

        use_sdp_java = True
        if use_sdp_java:
            self.log.debug("Using java internal SDP")
            self.use_sdp_java(intf)
        else:
            self.log.debug("Using libsdp LD_PRELOAD SDP")
            self.use_sdp_libsdp(intf)

    def use_sdp_java(self, intf, sdpdebug=True):
        """Use sdp through jdk 7"""
        if self.javaversion['major'] < 1 or self.javaversion['minor'] < 7:
            self.log.warn("Java SDP support requires at least JDK 1.7")
            return
        sdpconf = []
        netw = "%s/%s" % (intf[1], intf[3])
        portrange = "32000-*"
        sdpconf.append("connect %s %s" % (netw, portrange))
        sdpconf.append("bind %s %s" % (netw, portrange))

        ## add default general
        # (java sdp is a bit stupid; doesn't recognize a bind to 0.0.0.0 as valid part for configured bind subnet)
        ## - only for https(s) type connection
        #netw = "%s" % ('0.0.0.0')
        #portrange = "32000-*"  ##
        #sdpconf.append("connect %s %s" % (netw, portrange))
        #sdpconf.append("bind %s %s" % (netw, portrange))

        ## refpath: the tasktracker config option hjas to exists everywhere (shared fs or identical structure (eg localclient with same name (eg not the MPI rank))
        # refdir = '$%s_CONF_DIR'%self.daemonname.upper() does not work, tasktracker does not export it to the task jvm shell
        refdir = os.path.join(self.basedir, 'refdir')  # is part of basedir, so exists

        content = "\n".join(sdpconf + [''])

        fn_name = 'sdp.conf'

        sdpconf_fn = os.path.join(self.confdir, fn_name)
        fh = open(sdpconf_fn, 'w')
        fh.write(content)
        fh.close()

        refsdpconf_fn = os.path.join(refdir, fn_name)
        fh = open(refsdpconf_fn, 'w')
        fh.write(content)
        fh.close()

        self.log.debug(
            "Written sdp.conf %s with content %s" % (sdpconf_fn, content))

        refpath = '-Dcom.sun.sdp.conf=%s' % (refsdpconf_fn)  # use variable so this file always exists when task is executed
        fixedpath = '-Dcom.sun.sdp.conf=%s' % sdpconf_fn

        javaopts = Arguments([fixedpath,
                              '-Djava.net.preferIPv4Stack=true'])
        refjavaopts = Arguments([refpath,
                                 '-Djava.net.preferIPv4Stack=true'])

        if sdpdebug:
            ## add $$ for unique id
            debug_name = "sdp.debug.log.$$"
            debuglog = os.path.join("%s" % self.env_params['%s_LOG_DIR' %
                                    self.daemonname.upper()], debug_name)
            self.log.debug("Going to log sdp to %s" % debuglog)
            javaopts += Arguments(["-Dcom.sun.sdp.debug=%s" % (debuglog)])
            refjavaopts += Arguments(
                ["-Dcom.sun.sdp.debug=%s/%s" % (refdir, debug_name)])

        self.add_param('mapred.child.java.opts', refjavaopts)
        self.add_param(
            '%s_OPTS' % self.daemonname.upper(), javaopts, is_env=True)

    def use_sdp_libsdp(self, intf, sdpdebug=True):
        """Configure for libsdp SDP through LD_PRELOAD"""
        sdpconf = ['## HOD generated']

        loglvl = 9
        if sdpdebug:
            loglvl = 7
        debuglog = os.path.join("%s" % self.env_params['%s_LOG_DIR' %
                                self.daemonname.upper()], "sdp.debug.log")
        self.log.debug("Going to log sdp to %s" % debuglog)
        sdpconf.append('#log min-level %s destination file %s' % (loglvl, debuglog))  # logging disabled for now. causes issues with extra log info to stdout

        ## last entries, catch all
        softname = '*java*'
        portrange = '50020'  # '32000-65536' ## portrange, only datanodes will benefit ?
        netw = "%s/%s" % (intf[1], intf[3])
        sdpconf.append('use sdp server %s %s:%s' % (softname, netw, portrange))
        sdpconf.append('use sdp client %s %s:%s' % (softname, netw, portrange))

        content = '\n'.join(sdpconf + [''])  # add newline

        sdpconf_fn = os.path.join(self.confdir, 'sdp.conf')
        fh = open(sdpconf_fn, 'w')
        fh.write(content)
        fh.close()
        self.log.debug(
            "Written sdp.conf %s with content %s" % (sdpconf_fn, content))
        self.add_param('LIBSDP_CONFIG_FILE', sdpconf_fn, is_env=True)

        libsdp_fn = "libsdp.so"  # expect to find it in std library path!
        ldpreload = ':'.join(
            [libsdp_fn] + os.environ.get('LD_PRELOAD', '').split(':'))
        self.log.debug(
            "Added libsdp %s to LD_PRELOAD %s" % (libsdp_fn, ldpreload))
        self.add_param('LD_PRELOAD', ldpreload, is_env=True)
