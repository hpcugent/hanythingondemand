from hod.config.hadoopopts import HadoopOpts
from hod.config.hadoopcfg import HadoopCfg

from hod.commands.command import GenerateSshKey, RunSshd, KillPidFile

from hod.config.customtypes import Params, ParamsDescr, HostnamePort, Arguments

from vsc import fancylogger
fancylogger.setLogLevelDebug()

import re, os


CLIENT_OPTS = ParamsDescr({
})

CLIENT_SOCKS_OPTS = ParamsDescr({
    'hadoop.socks.server':[HostnamePort('localhost:10000'), 'Use this SOCKS server'],
    'hadoop.rpc.socket.factory.class.default':['org.apache.hadoop.net.SocksSocketFactory', 'Use SOCKS sockets']
})

CLIENT_SOCKS_ENV_OPTS = ParamsDescr({
    'HADOOP_OPTS':[Arguments(['-Dsun.net.spi.nameservice.provider.1="dns,sun"', '-Dsun.net.spi.nameservice.nameservers=']), 'Specify the DNS server Sun JDK will use']
})

class ClientCfg(HadoopCfg):
    """Client cfg"""
    def __init__(self, name='localclient'):
        HadoopCfg.__init__(self)
        self.name = name


class LocalClientOpts(ClientCfg, HadoopOpts):
    """Local client options"""
    def __init__(self, shared=None, basedir=None, name='localclient'):
        HadoopOpts.__init__(self, shared=shared, basedir=basedir)
        ClientCfg.__init__(self, name=name)

    def init_defaults(self):
        """Create the default list of params and description"""
        self.log.debug("Adding init defaults.")
        self.add_from_opts_dict(CLIENT_OPTS)


    def init_core_defaults_shared(self, shared):
        """Create the core default list of params and description"""
        if shared is None:
            shared = {}

        exclude_params = [r'\.dir$',
                          r'^mapred.local',
                          ]
        exclude_env_params = [r'_DIR$']


        ## make compiled regexp
        exclude_params = [re.compile(x) for x in exclude_params]
        exclude_env_params = [re.compile(x) for x in exclude_env_params]

        ## first parse the params from the (previously initiated) active work
        ## - they are updated in the order they are started (last)
        prev_params = ParamsDescr()
        prev_env_params = ParamsDescr()
        for act_work in self.shared_active_work:
            name = act_work['work_name']
            params = act_work.get('params', Params({}))
            env_params = act_work.get('env_params', Params({}))
            self.log.debug("Active work from %s params %s env_params %s" % (name, params, env_params))
            for k, v in params.items():
                for excl_k in exclude_params:
                    if not excl_k.search(k):
                        prev_params.update({k:[v, '']})
                        continue

            for k, v in env_params.items():
                for excl_k in exclude_env_params:
                    if not excl_k.search(k):
                        prev_env_params.update({k:[v, '']})
                        continue

        self.add_from_opts_dict(prev_params)
        self.add_from_opts_dict(prev_env_params, update_env=True)

        ## other passed params override the previous ones         
        self.log.debug("Adding init shared core params")
        self.add_from_opts_dict(shared.get('params', ParamsDescr({})))

        self.log.debug("Adding init shared core env_params")
        self.add_from_opts_dict(shared.get('env_params', ParamsDescr({})), update_env=True)


class RemoteClientOpts(LocalClientOpts):
    """Remote client options"""
    def __init__(self, shared=None, basedir=None):
        LocalClientOpts.__init__(self, shared=shared, basedir=basedir, name='remoteclient')

        self.pubkeys = []

        self.sshdstart = None
        self.sshdstop = None

    def init_core_defaults_shared(self, shared):
        LocalClientOpts.init_core_defaults_shared(self, shared)


        self.pubkeys = shared.get('pubkeys', [])

        self.log.debug("adding SOCKS config")
        self.add_from_opts_dict(CLIENT_SOCKS_OPTS)
        self.add_from_opts_dict(CLIENT_SOCKS_ENV_OPTS, update_env=True)

    def gen_ssh_cfg(self):
        """Make the sshd_config and the authorized_keys file"""
        sshd_fn = os.path.join(self.confdir, 'sshd_config')
        authkeys_fn = os.path.join(self.confdir, 'authorized_keys')
        hostkey_fn = os.path.join(self.confdir, 'key')
        pid_fn = os.path.join(self.confdir, 'pid')
        ssh_port = 12345

        txt = []
        txt.append("AuthorizedKeysFile %s" % authkeys_fn)
        txt.append("HostKey %s" % hostkey_fn)
        txt.append("Port %s" % ssh_port)
        txt.append("PidFile %s" % pid_fn)
        txt.append("PasswordAuthentication no")
        txt.append("ForceCommand '/bin/sleep inf'") ## is this enough or is the command still needed?
        txt.append("Protocol 2")
        txt.append("SyslogFacility USER")
        txt.append("StrictModes no")

        ## the sshd config
        content = "\n".join(txt + ['']) ## add newline
        self.log.debug("Creating sshd_config file %s with content %s" % (sshd_fn, content))
        try:
            fh = open(sshd_fn, 'w')
            fh.write(content)
            fh.close()
            self.log.debug("Written sshd_config file %s with content %s" % (sshd_fn, content))
        except OSError:
            self.log.exception("Failed to write sshd_config file %s with content %s" % (sshd_fn, content))


        ## the pubkeys
        ssh_key_prefix = ','.join(['command="/bin/sleep inf"', 'no-X11-forwarding', 'no-agent-forwarding', 'no-pty'])
        txt = ['# Initally generated ', "# prefix all manually added pubkkeys with '%s' !" % ssh_key_prefix]
        for key in self.pubkeys:
            txt.append("%s %s" % (ssh_key_prefix, key))

        content = "\n".join(txt + ['']) ## add newline
        self.log.debug("Creating authorized_keys file %s with content %s" % (authkeys_fn, content))
        try:
            fh = open(authkeys_fn, 'w')
            fh.write(content)
            fh.close()
            self.log.debug("Written authorized_keys file %s with content %s" % (authkeys_fn, content))
        except OSError:
            self.log.exception("Failed to write authorized_keys file %s with content %s" % (authkeys_fn, content))

        ## generate the priv/pub hostkey
        cmd = GenerateSshKey(hostkey_fn)
        cmd.run()

        self.log.debug("Preparing the sshd start from cfg file %s" % sshd_fn)
        self.sshdstart = RunSshd(sshd_fn)
        self.log.debug("Preparing the sshd kill from pid file %s" % pid_fn)
        self.sshdstop = KillPidFile(pid_fn)


    def make_opts_env_cfg(self):
        """Make the cfg file"""
        HadoopOpts.make_opts_env_cfg(self)

        ##
        self.gen_ssh_cfg()
