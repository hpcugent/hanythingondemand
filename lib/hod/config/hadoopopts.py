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
Hadoop options

http: // hadoop.apache.org / common / docs / current / core - default.html

## Better guide
http: // hadoop.apache.org / common / docs / current / cluster_setup.html

@author: Stijn De Weirdt
"""

import os
import shutil
import re
import pwd

from hod.config.customtypes import HdfsFs, Directories, Arguments, Params, ParamsDescr, UserGroup
from xml.dom import getDOMImplementation

from hod.config.hadoopcfg import HadoopCfg, which_exe


CORE_OPTS = ParamsDescr({
    'fs.default.name': [
        HdfsFs(':8020'),
        'FINAL The name of the default file system.  A URI whose scheme and authority'
        'determine the FileSystem implementation.  The uris scheme determines the'
        'config property (fs.SCHEME.impl) naming the FileSystem implementation class.'
        'The uris authority is used to determine the host, port, etc. for a filesystem.'
    ],
    'hadoop.tmp.dir': [
        Directories([None]),
        'FINAL Is used as the base for temporary kindoflist locally, and also in HDFS',
    ],
    'dfs.replication': [
        1,
        'FINAL Default block replication. The actual number of replications can be specified when the file is created.'
        'The default is used if replication is not specified in create time.',
    ],
    'fs.inmemory.size.mb': [
        200,
        'Larger amount of memory allocated for the in-memory filesystem used to merge map-outputs at the reduces.',
    ],
    'io.file.buffer.size': [128 * 1024, 'Size of read/write buffer used in SequenceFiles. (default 4kB)'],
    'io.sort.factor': [64, 'More streams merged at once while sorting files. (default 10)'],
    'io.sort.mb': [256, 'Higher memory - limit while sorting data. (default 100)'],
    'hadoop.rpc.socket.factory.class.default': [
        'org.apache.hadoop.net.StandardSocketFactory',
        'FINAL Force standard sockets for non-clients',
    ],
})

CORE_SECURITY_SERVICE = ParamsDescr({
    'security.refresh.policy.protocol.acl': [
        UserGroup(),
        'ACL for RefreshAuthorizationPolicyProtocol, used by the dfsadmin and mradmin commands to refresh the security'
        'policy in-effect.',
    ],
})


MYHADOOP_OPTS = ParamsDescr({
    'io.file.buffer.size': [128 * 1024, 'Size of read/write buffer'],
    'fs.inmemory.size.mb': [650, 'Size of in-memory FS for merging outputs'],
    'io.sort.mb': [650, 'Memory limit for sorting data'],

    #'dfs.replication': [ 2, 'Number of times data is replicated'],
    'dfs.block.size': [128 * 1024 * 1024, 'HDFS block size in bytes'],
    'dfs.datanode.handler.count': [64, 'Number of handlers to serve block requests'],

    'mapred.reduce.parallel.copies': [4, 'Number of parallel copies run by reducers'],
    'mapred.tasktracker.map.tasks.maximum': [4, 'Max map tasks to run simultaneously'],
    'mapred.tasktracker.reduce.tasks.maximum': [2, 'Max reduce tasks to run simultaneously'],
    'mapred.job.reuse.jvm.num.tasks': [1, 'Reuse the JVM between tasks'],
    'mapred.child.java.opts': [Arguments('-Xmx1024m'), 'Large heap size for child JVMs'],
})
## tuned options for sort900 benchmark
SORT900_OPTS = ParamsDescr({
    'dfs.block.size': [128 * 1024 * 1024, 'HDFS blocksize of 128MB for large file-systems.'],
    'dfs.namenode.handler.count': [40, 'More NameNode server threads to handle RPCs from large number of DataNodes.'],

    'mapred.reduce.parallel.copies': [
        20,
        'Higher number of parallel copies run by reduces to fetch outputs from very large number of maps.',
    ],
    'mapred.map.child.java.opts': [Arguments(['-Xmx512M']), 'Larger heapsize for child jvms of maps.'],
    'mapred.reduce.child.java.opts': [Arguments(['-Xmx512M']), 'Larger heapsize for child jvms of reduces.'],
    'io.sort.factor': [100, 'More streams merged at once while sorting files.'],
    'io.sort.mb': [200, 'Higher memory - limit while sorting data.'],

    'fs.inmemory.size.mb': [
        200,
        'Larger amount of memory allocated for the in-memory filesystem used to merge map-outputs at the reduces.',
    ],
    'io.file.buffer.size': [128 * 1024, 'Size of read/write buffer used in SequenceFiles.'],
})

## more tuning for the sort1400 benchmark
SORT1400_OPTS = ParamsDescr({
    'mapred.job.tracker.handler.count': [
        60,
        'More JobTracker server threads to handle RPCs from large number of TaskTrackers.',
    ],
    'mapred.reduce.parallel.copies': [50, ' '],
    'tasktracker.http.threads': [
        50,
        'More worker threads for the TaskTrackers http server. The http server is used by reduces to fetch intermediate'
        'map-outputs.',
    ],
    'mapred.map.child.java.opts': [Arguments(['-Xmx512M']), 'Larger heap-size for child jvms of maps.'],
    'mapred.reduce.child.java.opts': [Arguments(['-Xmx1024M']), 'Larger heap-size for child jvms of reduces.'],
})


#For example, To configure Namenode to use parallelGC, the following statement should be added in hadoop-env.sh :
#export HADOOP_NAMENODE_OPTS="-XX:+UseParallelGC ${HADOOP_NAMENODE_OPTS}"
HADOOP_ENV_OPTS = ParamsDescr({
    'HADOOP_CONF_DIR': [None, 'The directory where the config files are located. Default is HADOOP_PREFIX/conf.'],
    'HADOOP_LOG_DIR': [
        None,
        'The directory where the daemons log files are stored. They are automatically created if they dont exist.',
    ],
    'HADOOP_PID_DIR': [
        None,
        'The directory where the daemons pid files are stored. They are automatically created if they dont exist.',
    ],
    'HADOOP_HEAPSIZE': [
        1000,
        'The maximum amount of heapsize to use, in MB e.g. 1000MB. This is used to configure the heap size for the'
        'hadoop daemon. By default, the value is 1000MB.',
    ],
    'HADOOP_OPTS': [Arguments('-server'), 'Java options for all hadoop processes (-server should be default)']
})

## Don't set the niceness
##     'HADOOP_NICENESS' : [0, 'Run the daemons with nice factor.'],
##


class HadoopOpts(HadoopCfg):
    """Hadoop options class. Determine optimal default values and other explicit settings"""

    def __init__(self, shared=None, basedir=None):
        HadoopCfg.__init__(self)

        if shared is None:
            shared = {}
        shared.setdefault('other_work', {})
        shared.setdefault('active_work', {})

        self.shared_opts = shared
        self.log.debug("shared_opts %s" % self.shared_opts)

        self.basedir = basedir  # opts basedir

        self.confdir = None  # configdir (with eg core-site.xml)
        self.logdir = None
        self.piddir = None

        self.default_fsdefault = HdfsFs(':8020')   # default namenode

        self.envfilename = None  # will default to 'daemonname'-env.sh

        self.params = Params()  # these will become the default params
        self.description = Params()  # description info for the parameters (if any)

        self.env_params = Params()  # shell env_params file
        self.env_description = Params()  # shell env_params file

        self.security = True
        self.allowed_user = None
        self.allowed_groups = None

        self.set_default_funcs = [self.set_core_service_defaults, self.set_service_defaults]

        ## run intialisation
        self.init_core_defaults()

        if self.security:
            self.log.debug("Setting core security related options")
            self.init_core_security_defaults()
        else:
            self.log.debug("Not setting core security options")

        self.tuning = self.basic_tuning()

        self.init_defaults()

        if self.security:
            self.log.debug("Setting security related options")
            self.init_security_defaults()
        else:
            self.log.debug("Not setting security options")

        self.init_core_defaults_shared(shared)  # add the shared last (will override through update)

        self.attrs_to_share = ['params', 'env_params', 'basedir', 'confdir', 'hadoop', 'hadoophome', 'java', 'javahome']

    def init_core_defaults(self):
        """Create the core default list of params and description"""
        self.log.debug("Adding init core defaults")
        self.add_from_opts_dict(CORE_OPTS)

        self.log.debug("Adding init core env_params. Adding HADOOP_ENV_OPTS %s" % HADOOP_ENV_OPTS)
        self.add_from_opts_dict(HADOOP_ENV_OPTS, update_env=True)

    def init_core_security_defaults(self):
        """Add core security options"""
        self.add_from_opts_dict(CORE_SECURITY_SERVICE)

    def init_security_defaults(self):
        """Add security options"""
        self.log.debug("init security defaults not implemented")

    def init_core_defaults_shared(self, shared):
        """Create the core default list of params and description"""
        if shared is None:
            shared = {}
        self.log.debug("Adding init shared core params")
        self.add_from_opts_dict(shared.get('params', ParamsDescr({})))

        self.log.debug("Adding init shared core env_params")
        self.add_from_opts_dict(shared.get('env_params', ParamsDescr({})), update_env=True)

    def init_defaults(self):
        """Create the default list of params and description"""
        self.log.warn("Adding init defaults. Not implemented here.")

    def set_defaults(self):
        """Set some defaults if required"""
        self.log.debug("set_defaults")
        missing = self.check_params_or_env(do_error=False)
        self.log.debug("set_defaults missing params %s" % missing)
        missingenv = self.check_params_or_env(do_error=False, check_env=True)
        self.log.debug("set_defaults missing env %s" % missingenv)

        for mis in missing + missingenv:
            not_found_mis = True
            for set_def in self.set_default_funcs:
                if not_found_mis:
                    not_found_mis = set_def(mis)
            if not_found_mis:
                self.log.warn("end of set_defaults mis %s not found" % mis)

    def set_core_service_defaults(self, mis):
        """Set some defaults if required"""
        self.log.debug("Setting core servicedefaults for %s" % mis)
        if mis in ('hadoop.tmp.dir',):
            self.log.debug("%s not set. using basedir %s" % (mis, self.basedir))
            self.params[mis] = self.basedir
        elif mis in ('fs.default.name',):
            if None in self.default_fsdefault:
                self.log.error("%s not set and no default_fsdefault set" % mis)
            else:
                self.log.debug("%s not set. using %s" % (mis, self.default_fsdefault))
                self.params[mis] = "%s" % self.default_fsdefault
        elif mis.startswith('security.') and mis.endswith('.protocol.acl'):
            ## security protocol acl (ie a USerGroup)
            tmpuser = pwd.getpwuid(os.getuid()).pw_name
            self.log.debug("core security defaults: None found in mis %s (value %s)." % (mis, self.params[mis]))
            if None in self.params[mis].users:
                self.log.debug("None found in mis %s users. Adding user %s" % (mis, tmpuser))
                self.params[mis].add_users(tmpuser)

        elif mis in ('HADOOP_LOG_DIR',):
            self.log.debug("%s not set. using logdir %s" % (mis, self.logdir))
            self.env_params[mis] = self.logdir
        elif mis in ('HADOOP_PID_DIR',):
            self.log.debug("%s not set. using piddir %s" % (mis, self.piddir))
            self.env_params[mis] = self.piddir
        elif mis in ('HADOOP_CONF_DIR',):
            self.log.debug("%s not set. using confdir %s" % (mis, self.confdir))
            self.env_params[mis] = self.confdir
        elif mis in ('HADOOP_OPTS',):
            self.log.debug("%s not set. using nothing (value is %s)" % (mis, self.env_params[mis]))
        else:
            self.log.warn("Variable %s not found in core service defaults" % mis)  # TODO is warn enough?
            return True  # not_mis_found

    def set_service_defaults(self, mis):
        """Set service specific default"""
        self.log.warn("Setting servicedefaults. Not implemented here. Skipping %s" % mis)
        return True  # not_mis_found

    def add_param(self, name, value, is_env=False):
        """Add value to name (adding, not overriding)"""
        whattxt = "name %s value %s (type %s)" % (name, value, value.__class__.__name__)
        if is_env:
            where = self.env_params
            self.log.debug("Adding to environment params %s" % whattxt)
        else:
            where = self.params
            self.log.debug("Adding to params %s" % whattxt)

        if name in where:
            self.log.debug("Previous value %s (type %s)" % (where[name], where[name].__class__.__name__))
            where[name] += value
            self.log.debug("Added value %s (previous found). New value %s  (type %s)" % (value, where[name], where[name].__class__.__name__))
        else:
            where[name] = value
            self.log.debug("Add: set value %s (no previous found). New value %s (type %s)" % (value, where[name], where[name].__class__.__name__))

    def set_param(self, name, value, is_env=False):
        """Set value to name (adding, not overriding)"""
        if is_env:
            where = self.env_params
            self.log.debug("Setting to environment params name %s value %s" % (name, value))
        else:
            where = self.params
            self.log.debug("Setting to params %s value %s" % (name, value))

        where[name] = value
        self.log.debug("Set value %s. New value %s" % (value, where[name]))

    def add_from_opts_dict(self, optsdict, update_env=False):
        """Parse an opts dictionary and update params and description (overrides values!)"""
        self.log.debug("add_from_opts_dict optsdict %s" % optsdict)
        params = Params()
        description = Params()
        for k, v in optsdict.items():
            if type(v) in (list, tuple,):
                if len(v) == 2:
                    params[k] = v[0]
                    description[k] = v[1]
                else:
                    self.log.error('Unknown length of list of value %s for key %s (optsdict %s)' % (v, k, optsdict))
            elif type(v) == str:
                ## only description, no value (esp not None)
                description[k] = v
            else:
                self.log.error('Unknown format of value %s for key %s (optsdict %s)' % (v, k, optsdict))

        self.log.debug("Going to update with params %s and description %s" % (params, description))
        if update_env:
            self.env_params.update(params)
            self.env_description.update(description)
        else:
            self.params.update(params)
            self.description.update(description)
            self.log.debug("New params %s and description %s" % (self.params, self.description))

    def check_params_or_env(self, do_error=True, check_env=False):
        """Check for params or env_params containing None"""
        tocheck = []
        if check_env:
            check_what = self.env_params
            typ = 'env_params'
        else:
            check_what = self.params
            typ = 'params'

        for k, v in check_what.items():
            is_not_ok = False
            try:
                is_not_ok = None in v
            except TypeError:
                is_not_ok = None is v
            if is_not_ok:
                self.log.debug("None found for %s %s with value %s (type %s)" % (typ, k, v, v.__class__.__name__))
                tocheck.append(k)
        if tocheck:
            if do_error:
                ## when call as standalone sanity check
                self.log.error("None found for %s %s " % (typ, tocheck))
            else:
                self.log.debug("None found for %s %s " % (typ, tocheck))
        return tocheck

    def basic_tuning(self):
        """Some basic tuning options to add"""
        s1400 = ParamsDescr()
        s1400.update(SORT900_OPTS)
        s1400.update(SORT1400_OPTS)
        self.tuning = {
            'sort900': SORT900_OPTS,
            'sort1400': s1400,
        }
        self.log.debug("Made basic preconfig tuning params %s" % self.tuning)

    def create_xml_element(self, doc, name, value, description, final=False):
        """Create the xml element"""
        self.log.debug("Creating element with name %s value %s description %s final %s doc %s" % (name, value, description, final, doc))
        prop = doc.createElement("property")

        nameP = doc.createElement("name")
        string = doc.createTextNode(name)
        nameP.appendChild(string)

        valueP = doc.createElement("value")
        string = doc.createTextNode("%s" % value)  # explicit cast to string for special types
        valueP.appendChild(string)

        if final:
            finalP = doc.createElement("final")
            string = doc.createTextNode("true")
            finalP.appendChild(string)

        if description:
            descP = doc.createElement("description")
            string = doc.createTextNode(description)
            descP.appendChild(string)

        prop.appendChild(nameP)
        prop.appendChild(valueP)
        if final:
            prop.appendChild(finalP)
        if description:
            prop.appendChild(descP)

        return prop

    def prep_dir(self, directory, basedirsubdir='default'):
        """Prepare a directory"""
        if directory is None or None in directory:
            if self.basedir is None:
                self.log.error("basedir is None")
            else:
                directory = os.path.join(self.basedir, basedirsubdir)  # default based on basedir
                self.log.debug("Set dir to %s" % directory)

        if not os.path.isdir(directory):
            self.log.debug("dir %s not found. Creating" % directory)
            try:
                os.makedirs(directory)
            except OSError:
                self.log.exception("Failed to create dir %s" % directory)

        return directory

    def prep_conf_dir(self):
        """Prepare config/log/pid directory"""
        self.log.debug("Prepare config and other dirs")
        self.confdir = self.prep_dir(self.confdir, 'config')
        self.log.debug("confdir set to %s" % self.confdir)

        self.logdir = self.prep_dir(self.logdir, 'logs')
        self.log.debug("logdir set to %s" % self.logdir)

        self.piddir = self.prep_dir(self.piddir, 'pid')
        self.log.debug("piddir set to %s" % self.piddir)

    def gen_conf_xml_new(self):
        """Generate config xml files"""
        self.log.debug("Generate and write the xml configs")
        ## based upon the files in hadoopDir/etc/hadoop
        ## - regexp strings (will be compiled in next step
        ## - all unmatched go to defaultdestination

        defaultdestination = 'core-site'  # no regexps for this

        ## mapping based on share/hadoop/templates/conf
        ## whitelist
        dest2whitereg = {
            'capacity-scheduler': [r'^mapred\.capacity-scheduler'],
            'mapred-queue-acls': [r'^mapred\.queue.*?\.acl'],
            'hdfs-site': [r'^dfs\.'],
            'mapred-site': [r'^mapred(uce)?\.', r'^jetty\.connector', r'^tasktracker\.', r'^job\.end\.retry\.',
                            r'^hadoop\.job\.history', r'^io\.(sort|map)\.', r'^jobclient\.output\.filter',
                            r'^keep.failed.task.files',
                            ],
            'hadoop-policy': [r'^security\.'],
            'hbase-site': [r'^hbase\.']
        }
        ## blacklist
        dest2blackreg = {
            'mapred-site': dest2whitereg['capacity-scheduler'] + dest2whitereg['mapred-queue-acls'],
        }

        ## default xsl
        defaultxsl = 'configuration'

        ## try to copy the default xsl to the config dir.
        ## - if not: don't set it
        if self.hadoophome:
            defaultxslfn = "%s.xsl" % defaultxsl
            defaultxslpath = os.path.join(self.hadoophome, 'etc', 'hadoop', defaultxslfn)
            if os.path.exists(defaultxslpath):
                newxslpath = os.path.join(self.confdir, defaultxslfn)
                try:
                    shutil.copy(defaultxslpath, newxslpath)
                    self.log.debug("Copied defaultxsl from %s to %s" % (defaultxslpath, newxslpath))
                except:
                    ## do nothing
                    self.log.exception("Failed to Copy defaultxsl from %s to %s" % (defaultxslpath, newxslpath))
                    defaultxsl = ''
        else:
            self.log.debug("hadoophome not set. ignoring default xsl")
            defaultxsl = ''

        ## make fullDict map with destination -> list of keys
        alldests = [defaultdestination]
        dest2whiteregcomp = {}
        for dest, regtxts in dest2whitereg.items():
            dest2whiteregcomp[dest] = []
            for regtxt in regtxts:
                dest2whiteregcomp[dest].append(re.compile(regtxt))
            if not dest in alldests:
                alldests.append(dest)

        dest2blackregcomp = {}
        for dest, regtxts in dest2blackreg.items():
            dest2blackregcomp[dest] = []
            for regtxt in regtxts:
                dest2blackregcomp[dest].append(re.compile(regtxt))
            if not dest in alldests:
                alldests.append(dest)

        fullDict = {}
        self.log.debug("Following parameters are set %s" % self.params)
        for k in self.params.keys():
            for dest in alldests:
                if dest in dest2blackregcomp and any([r.search(k) for r in dest2blackregcomp[dest]]):
                    ## found in blacklist. skip it.
                    continue
                if dest in dest2whiteregcomp and any([r.search(k) for r in dest2whiteregcomp[dest]]):
                    if not dest in fullDict:
                        fullDict[dest] = []
                    fullDict[dest].append(k)
            ## if not in any of the matched values, add to default
            if not any([k in v for v in fullDict.values()]):
                if not defaultdestination in fullDict:
                    fullDict[defaultdestination] = []
                fullDict[defaultdestination].append(k)

        for dest in fullDict.keys():
            fn = "%s.xml" % dest
            self.log.debug("Writing to dest %s params %s" % (fn, fullDict[dest]))

            implementation = getDOMImplementation()
            doc = implementation.createDocument('', 'configuration', None)
            topElement = doc.documentElement
            if defaultxsl and len(defaultxsl) > 0:
                stylesheet = doc.createProcessingInstruction("xml-stylesheet", 'type="text/xsl" href="%s"' % defaultxslfn)
                doc.insertBefore(stylesheet, topElement)

            comment = doc.createComment("This is an auto-generated %s, do not modify" % fn)
            doc.insertBefore(comment, topElement)

            # generate the xml elements
            for name in fullDict[dest]:
                value = self.params[name]
                description = self.description.get(name, None)
                final = (description is not None) and (description.startswith('FINAL'))

                typ = type(value)
                if  typ in (list, tuple):
                    value = list(value)
                else:
                    value = [value]

                for realvalue in value:
                    ## TODO: check if it is better to loop inside create_xml_element
                    try:
                        prop = self.create_xml_element(doc, name, realvalue, description, final)
                    except TypeError:
                        raise TypeError("Wrong type for name %s value '%s' description '%s' final %s" % (name, realvalue, description, final))

                    topElement.appendChild(prop)

            siteFilename = os.path.join(self.confdir, fn)
            self.log.debug("Writing dest %s to %s" % (fn, siteFilename))
            sitefile = file(siteFilename, 'w')
            ## write from document
            ## - no prettyprint to avoid indentation whitespaces in the values
            doc.writexml(sitefile, indent=" " * 0, addindent=" " * 0, newl="\n" * 0)
            sitefile.close()

    def gen_conf_env(self):
        """Create the shell env config file"""
        txt = ["# Generated with HOD", '']
        for variable, value in self.env_params.items():
            comment = self.env_description.get(variable, None)
            if comment:
                line = '# export %s ## %s' % (variable, comment)
                txt.append(line)
            line = 'export %s="%s"' % (variable, value)
            self.log.debug("add to env_params conf file variable %s value %s (type %s)" % (variable, value, value.__class__.__name__))
            txt.append(line)

        txt += ['']  # end with newline

        if self.envfilename is None:
            self.envfilename = "%s-env.sh" % self.daemonname

        envfn = os.path.join(self.confdir, self.envfilename)
        content = "\n".join(txt)
        try:
            fh = open(envfn, 'w')
            fh.write(content)
            fh.close()
            self.log.debug("Written env_params file %s with content %s" % (envfn, content))
        except OSError:
            self.log.exception("Failed to write env_params file %s with content %s" % (envfn, content))

    def params_env_sanity_check(self):
        """Run sanity check on params and env variables"""
        self.log.debug("params sanity check")
        self.check_params_or_env()  # sanity check
        self.log.debug("env_params sanity check")
        self.check_params_or_env(check_env=True)

        ## more detailed checks
        for param, val in self.params.items():
            if val.__class__.__name__ in ('Directories',):
                self.log.debug("Run check on param %s instance %s (type %s)" % (param, val, val.__class__.__name__))
                val.check()

        for param, val in self.env_params.items():
            if val.__class__.__name__ in ('Directories',):
                self.log.debug("Run check on env_param %s instance %s (type %s)" % (param, val, val.__class__.__name__))
                val.check()

    def pre_run_any_service(self):
        """To be run before any service start/wait/stop"""
        varname = 'HADOOP_CONF_DIR'
        varvalue = self.confdir
        self.log.debug("set %s in environment to %s" % (varname, varvalue))
        os.putenv(varname, varvalue)

    def set_niceness(self, nicelevel=5, ioniceclass=2, ionicelevel=9, hwlocbindopts=None, varname='HADOOP_NICENESS'):
        """Set the HADOOP_NICENESS. (Due to bug in HADOOP_NICENESS in start scripts, this actually works"""
        ionice = which_exe('ionice')
        if ionice:
            ionice_opt = [ionice, '-c', "%d" % ioniceclass]
            if ioniceclass in (2, 3,):
                ionice_opt += ['-n', '%d' % ionicelevel]
            else:
                self.log.debug("ioniceclass %s not 2 or 3; ignoring ionicelevel %s" % (ioniceclass, ionicelevel))
            self.log.debug('ionice found, running with %s' % ionice_opt)
        else:
            ionice_opt = []
            self.log.warn('ionice not found, ignoring ionice options')

        hwlocbind = which_exe('hwloc-bind')
        if hwlocbind:
            if hwlocbindopts:
                if type(hwlocbindopts) == str:
                    hwlocbindopts = [hwlocbindopts]
                hwloc_opt = [hwlocbind] + hwlocbindopts
                self.log.debug('hwlocbind found, running with %s' % hwloc_opt)
            else:
                hwloc_opt = []
                self.log.debug("hwloc-bind found, but not opts set")
        else:
            hwloc_opt = []
            self.log.warn('hwloc-bind not found, ignoring hwlocbind options')

        varvalue = " ".join(["%d" % nicelevel] + ionice_opt + hwloc_opt)
        self.log.debug("set %s in environment to %s" % (varname, varvalue))
        os.putenv(varname, varvalue)

    def make_opts_env_defaults(self):
        """Set the defaults"""
        self.log.debug("Prepare configdir")
        self.prep_conf_dir()

        nr_iter = 3
        for x in range(nr_iter):
            self.log.debug("Setting defaults iter %s of %s" % (x, nr_iter))
            self.set_defaults()   # set the default on missing values in params

    def make_opts_env_cfg(self):
        """Make the cfg file"""
        self.log.debug("make_cfg Making the config files")

        self.params_env_sanity_check()

        self.log.debug("start writing files")
        self.gen_conf_xml_new()  # write xml files
        self.gen_conf_env()  # create the env.sh file
