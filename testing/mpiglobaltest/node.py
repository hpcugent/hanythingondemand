#!/usr/bin/env python
#
# Copyright 2012 Stijn De Weirdt
# 
# This file is part of HanythingOnDemand,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
from vsc import fancylogger
fancylogger.setLogLevelDebug()

import re, os, socket

class Node:
    """Detect localnode properties"""
    def __init__(self):
        self.log = fancylogger.getLogger(self.__class__.__name__)

        self.fqdn = 'localhost' ## base fqdn hostname
        self.network = [] ## all possible IPs

        self.pid = -1
        self.cores = -1
        self.usablecores = None

        self.topology = [0] ## default topology plain set

    def __str__(self):
        return "FQDN %s PID %s" % (self.fqdn, self.pid)

    def go(self, ret=True):
        """A wrapper around some common functions"""
        self.get_hostname()
        self.get_network()

        self.get_pid()
        self.cores_on_this_node()
        self.get_cpuset()

        self.get_topology()

        if ret:
            descr = {'fqdn':self.fqdn,
                   'network':self.network,
                   'pid':self.pid,
                   'cores':self.cores,
                   'usablecores':self.usablecores,
                   'topology':self.topology,
                   }
            return descr

    def get_hostname(self):
        """Return a system's true FQDN rather than any aliases, which are
           occasionally returned by socket.gethostname."""

        fqdn = None
        me = os.uname()[1]
        nameInfo = socket.gethostbyname_ex(me)
        nameInfo[1].append(nameInfo[0])
        for name in nameInfo[1]:
            if name.count(".") and name.startswith(me):
                fqdn = name
        if fqdn == None:
            fqdn = me

        self.fqdn = fqdn
        self.log.debug("Found fqdn %s" % self.fqdn)

    def get_network(self, cidrmask=None, domainmask=None, hostmask=None, devmask=None, cidrordomainmask=None, inputtxt='', up=True):
        """
        Get first matching IP. Input is from 'ip addr show'
        - up: Boolean, interface up
        - cidrmask: netmask mask to match eg 1.2.3.4/5
        - domainmask: hostname of ip endswith domainmask
        - hostmask: hostname of ip startswith hostmask
        - devmask: device name startswith
        - cidrordomainmask: will be determined if this is a cidr or domain mask
        
        To be replaced by netifaces and/or netaddr
        """

        if cidrordomainmask:
            if '/' in cidrordomainmask:
                cidrmask = cidrordomainmask
            else:
                domainmask = cidrordomainmask

        ipCommand = '/sbin/ip'
        if os.path.exists(ipCommand) and not inputtxt:
            from subprocess import Popen, PIPE ## TODO replace with proper command
            inputtxt = Popen([ipCommand, "addr", "show"], stdout=PIPE).communicate()[0]

        if not inputtxt:
            ## forced old behaviour (eg non-linux systems?)
            if not self.fqdn in self.network:
                self.network.append(self.fqdn)
            self.log.error("%s addr show returned no output. Using %s as network" % (ipCommand, self.network))
            return

        regdev = re.compile(r"^(?:\d+\s*:\s*(\S+)\s*:\s*<(\S+)>.*((?:\n\s.*)+))", re.M)
        regipv4 = re.compile(r"^\s+inet\s+(\d+(?:\.\d+){3})/(\d+)", re.M)

        def address_in_network(ip, net):
            "Is an address in a network"
            ## from http://stackoverflow.com/questions/819355/how-can-i-check-if-an-ip-is-in-a-network-in-python
            import struct
            def calc_dotted_netmask(mask):
                bits = 0
                for i in xrange(32 - mask, 32):
                    bits |= (1 << i)
                return "%d.%d.%d.%d" % ((bits & 0xff000000) >> 24, (bits & 0xff0000) >> 16, (bits & 0xff00) >> 8 , (bits & 0xff))

            endianness = '=L'
            ipaddr = struct.unpack(endianness, socket.inet_aton(ip))[0]
            netaddr, bits = net.split('/')
            netmask = struct.unpack('=L', socket.inet_aton(calc_dotted_netmask(int(bits))))[0]
            network = struct.unpack('=L', socket.inet_aton(netaddr))[0] & netmask
            return (ipaddr & netmask) == (network & netmask)


        for match in regdev.finditer(inputtxt):
            dev = match.group(1)
            if devmask and not dev.startswith(devmask):
                self.log.debug("dev %s does not match devmask %s" % (dev, devmask))
                continue

            state = match.group(2).split(',')
            if up and not 'UP' in state:
                ## interface is not up
                self.log.debug("dev %s state is not up: %s" % (dev, state))
                continue

            for ipv4match in regipv4.finditer(match.group(3)):
                ip = ipv4match.group(1)
                self.log.debug('Found ip %s' % ip)

                if cidrmask and not address_in_network(ip, cidrmask):
                    self.log.debug("dev %s ipv4 addr %s does not match cidrmask %s" % (dev, ip, cidrmask))
                    continue

                try:
                    name = socket.gethostbyaddr(ip)[0]
                    self.log.debug("Found name %s for ip %s" % (name, ip))
                except:
                    ## can't resolve name
                    self.log.debug("dev %s ipv4 addr %s can't resolve name." % (dev, ip))
                    name = None

                if name is not None and domainmask and not name.endswith(domainmask):
                    self.log.debug("dev %s ipv4 addr %s name %s doesn't end with domainmask %s." % (dev, ip, name, domainmask))
                    continue
                if name is not None and hostmask and not name.startswith(hostmask):
                    self.log.debug("dev %s ipv4 addr %s name %s doesn't start with hostmask %s." % (dev, ip, name, hostmask))
                    continue

                if name is None:
                    name = ip
                    self.log.debug("Using ip %s as name." % (ip))

                if not name in self.network:
                    self.log.debug("Adding name %s to network" % name)
                    self.network.append(name)

        self.log.debug("Found networks %s" % self.network)


    def get_pid(self):
        """Get the pid"""
        self.pid = os.getpid()
        self.log.debug("Found PID %s" % self.pid)

    def cores_on_this_node(self):
        """Get details from /proc/cpuinfo"""
        fn = '/proc/cpuinfo'
        regcores = re.compile(r"^processor\s*:\s*\d+\s*$", re.M)
        num = len(regcores.findall(file(fn).read()))

        self.log.debug("coresonthisnode: found %s cores" % num)
        self.cores = num

    def get_cpuset(self):
        """Detect presence of a cpuset"""
        if self.cores < 1:
            self.cores_on_this_node()
        self.usablecores = range(self.cores)

        cpusetmntpt = '/dev/cpuset' ## should be mounted TODO check mount                                                                                            
        myproccpuset = "/proc/%s/cpuset" % self.pid

        if not os.path.isdir(cpusetmntpt):
            self.log.debug("No cpuset mountpoint %s found" % (cpusetmntpt))
        elif not os.path.isfile(myproccpuset):
            self.log.debug("No proc cpuset %s found" % (myproccpuset))
        else:
            try:
                mycpusetsuffix = open(myproccpuset).read().strip().lstrip('/')
                cpusetfn = os.path.join(cpusetmntpt, mycpusetsuffix, 'cpus')
                if os.path.isfile(cpusetfn):
                    mycpus = [x.split('-') for x in open(cpusetfn).read().strip().split(',')]
                    cpst = []
                    for cpu in mycpus:
                        if len(cpu) == 1:
                            cpst += cpu
                        else:
                            cpst += range(int(cpu[0]), int(cpu[1]) + 1)
                    self.usablecores = [int(x) for x in cpst]
                    self.log.debug("Found cpuset %s" % (cpusetfn))
                else:
                    self.log.error("Found proccpuset %s but no cpus file %s" % (myproccpuset, cpusetfn))
            except IOError:
                self.log.exception("Failed to cpuset files")

        self.log.debug("Using cores %s" % (self.usablecores))

    def get_topology(self):
        """Somehow make a map of the network or other relevant topology.
            Topology returned is a list. 
            Example 8 nodes:
            Toplogy example 1: all nodes are in same rack behind same switch. There is no actual additional structure, so topology is [0]
                    example 2: 4 nodes in rack 0, 4 nodes in rack 1. Per rack, all nodes behind 1 switch. Topology is [0] or [1] (switches add no extra structure)
                    example 3: same as example 2, but now the first 2 nodes are behind 1 switch, as are the remaining 2 nodes: topology now is [0,0], [0,1], [1,0] or [1,1]    
                    ...
        """
        pass

if __name__ == '__main__':
    n = Node()
    descr = n.go()
    print descr
