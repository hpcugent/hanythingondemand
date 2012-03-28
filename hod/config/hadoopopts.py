"""
Hadoop options

http: // hadoop.apache.org / common / docs / current / core - default.html

## Better guide
http: // hadoop.apache.org / common / docs / current / cluster_setup.html
"""

from hod.config.types import *
import os, shutil, re
from xml.dom import getDOMImplementation

from vsc import fancylogger
fancylogger.setLogLevelDebug()

from hod.config.hadoopcfg import HadoopCfg


CORE_OPTS = {
    'fs.default.name' : [HostnamePort(), 'The name of the default file system.  A URI whose scheme and authority determine the FileSystem implementation.  The uris scheme determines the config property (fs.SCHEME.impl) naming ' + \
                        'the FileSystem implementation class.  The uris authority is used to determine the host, port, etc. for a filesystem.'],
    'hadoop.tmp.dir' : [Directories([None]), 'Is used as the base for temporary kindoflist locally, and also in HDFS'],
}


## tuned options for sort900 benchmark
SORT900_OPTS = {
    'dfs.block.size':[134217728, 'HDFS blocksize of 128MB for large file-systems.'],
    'dfs.namenode.handler.count':  [40, 'More NameNode server threads to handle RPCs from large number of DataNodes.'],

    'mapred.reduce.parallel.copies':[20, 'Higher number of parallel copies run by reduces to fetch outputs from very large number of maps.'],
    'mapred.map.child.java.opts':[Arguments(['-Xmx512M']), 'Larger heapsize for child jvms of maps.'],
    'mapred.reduce.child.java.opts':[Arguments(['-Xmx512M']), 'Larger heapsize for child jvms of reduces.'],
    'io.sort.factor':[100, 'More streams merged at once while sorting files.'],
    'io.sort.mb':[200, 'Higher memory - limit while sorting data.'],

    'fs.inmemory.size.mb':[200, 'Larger amount of memory allocated for the in-memory filesystem used to merge map-outputs at the reduces.'],
    'io.file.buffer.size':[131072, 'Size of read/write buffer used in SequenceFiles.'],
}

## more tuning for the sort1400 benchmark
SORT1400_OPTS = {
    'mapred.job.tracker.handler.count':[60, 'More JobTracker server threads to handle RPCs from large number of TaskTrackers.'],
    'mapred.reduce.parallel.copies':[50, ' '],
    'tasktracker.http.threads':[50, 'More worker threads for the TaskTrackers http server. The http server is used by reduces to fetch intermediate map-outputs.'],
    'mapred.map.child.java.opts':[Arguments(['-Xmx512M']), 'Larger heap-size for child jvms of maps.'],
    'mapred.reduce.child.java.opts':[Arguments(['-Xmx1024M']), 'Larger heap-size for child jvms of reduces.'],
}


#For example, To configure Namenode to use parallelGC, the following statement should be added in hadoop-env.sh :
#export HADOOP_NAMENODE_OPTS="-XX:+UseParallelGC ${HADOOP_NAMENODE_OPTS}"
HADOOP_ENV_OPTS = {
    'HADOOP_LOG_DIR': [Directories([None]), 'The directory where the daemons log files are stored. They are automatically created if they dont exist.'],
    'HADOOP_HEAPSIZE': [1000, 'The maximum amount of heapsize to use, in MB e.g. 1000MB. This is used to configure the heap size for the hadoop daemon. By default, the value is 1000MB.'],
}


class HadoopOpts(HadoopCfg):
    """Hadoop options class. Determine optimal default values and other explicit settings"""

    def __init__(self, basedir=None):
        HadoopCfg.__init__(self)

        self.basedir = basedir ## opts basedir

        self.confdir = None## configdir (with eg core-site.xml)

        self.default_fsdefault = None  ## default namenode

        self.params = {} ## these will become the default params
        self.description = {} ## description info for the parameters (if any)

        self.set_default_funcs = [self.set_core_service_defaults, self.set_service_defaults]

        self.init_core_defaults()

        self.tuning = self.basic_tuning()

        self.init_defaults()


    def init_core_defaults(self):
        """Create the core default list of params and description"""
        self.log.debug("Adding core_defaults")
        self.add_from_opts_dict(CORE_OPTS)

    def init_defaults(self):
        """Create the default list of params and description"""
        self.log.warn("Adding init defaults. Not implemented here.")

    def set_defaults(self):
        """Set some defaults if required"""
        missing = self.check_params(do_error=False)

        for mis in missing:
            for set_def in self.set_default_funcs:
                set_def(mis)

    def set_core_service_defaults(self, mis):
        """Set some defaults if required"""
        self.log.debug("Setting core servicedefaults. Not implemented here. Skipping %s" % mis)
        if mis in ('hadoop.tmp.dir',):
            self.log.debug("%s not set. using basedir %s" % (mis, self.basedir))
            self.params[mis] = self.basedir
        elif mis in ('fs.default.name',):
            if self.default_fsdefault is None:
                self.log.error("%s not set and no default_fsdefault set" % mis)
            else:
                self.log.debug("%s not set. using %s" % (mis, self.default_fsdefault))
                self.params[mis] = self.default_fsdefault

    def set_service_defaults(self, mis):
        """Set service specific default"""
        self.log.warn("Setting servicedefaults. Not implemented here. Skipping %s" % mis)

    def add_from_opts_dict(self, optsdict):
        """Parse an opts dictionary and update params and description (overrides values!)"""
        params = {}
        description = {}
        for k, v in optsdict.items():
            if type(v) in (list, tuple,):
                if len(v) == 2:
                    params[k] = v[0]
                    description[k] = v[1]
                else:
                    self.log.error('Unknown length of list of value %s for key %s (optsdict %s)' % (v, k, optsdict))
            elif type(v) == str:
                ## only description, no value (esp not None)
                self.description[k] = v
            else:
                self.log.error('Unknown format of value %s for key %s (optsdict %s)' % (v, k, optsdict))

        self.log.debug("Going to update with params %s and description %s" % (params, description))
        self.params.update(params)
        self.description.update(description)
        self.log.debug("New params %s and description %s" % (self.params, self.description))

    def check_params(self, do_error=True):
        """Check for params containing None"""
        tocheck = []
        for k, v in self.params.items():
            is_not_ok = False
            try:
                is_not_ok = None in v
            except TypeError:
                is_not_ok = None is v
            if is_not_ok:
                self.log.debug("None found for param %s with value %s" % (k, v))
                tocheck.append(k)
        if tocheck:
            if do_error:
                ## when call as standalone sanity check
                self.log.error("None found for params %s " % (tocheck))
            else:
                self.log.debug("None found for params %s " % (tocheck))
        return tocheck

    def basic_tuning(self):
        """Some basic tuning options to add"""
        s1400 = {}
        s1400.update(SORT900_OPTS)
        s1400.update(SORT1400_OPTS)
        self.tuning = {'sort900' : SORT900_OPTS,
                       'sort1400' : s1400,
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
        string = doc.createTextNode("%s" % value) ## explicit cast to string for special types
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

    def gen_conf_xml_new(self):
        """Generate config xml files"""
        self.log.debug("Generate and write the xml configs")
        ## based upon the files in hadoopDir/etc/hadoop
        ## - regexp strings (will be compiled in next step
        ## - all unmatched go to defaultdestination
        if self.confdir is None:
            if self.basedir is None:
                self.log.error("basedir is None")
            else:
                self.confdir = os.path.join(self.basedir, 'config') ## default based on basedir

        if not os.path.isdir(self.confdir):
            self.log.debug("confidir %s not found. Creating" % self.confdir)
            try:
                os.makedirs(self.confdir)
            except OSError:
                self.log.exception("Failed to create confdir %s" % self.confdir)


        defaultdestination = 'core-site' ## no regexps for this

        ## mapping based on share/hadoop/templates/conf
        ## whitelist
        dest2whitereg = {'capacity-scheduler':[r'^mapred\.capacity-scheduler'],
                         'mapred-queue-acls':[r'^mapred\.queue.*?\.acl'],
                         'hdfs-site':[r'^dfs\.'],
                         'mapred-site':[r'^mapred(uce)?\.', r'^jetty\.connector', r'^tasktracker\.', r'^job\.end\.retry\.',
                                        r'^hadoop\.job\.history', r'^io\.(sort|map)\.'
                                        r'^jobclient\.output\.filter', r'^keep.failed.task.files', ],
                         'hadoop-policy':[r'^security\.'],
                       }
        ## blacklist
        dest2blackreg = {'mapred-site':dest2whitereg['capacity-scheduler'] + dest2whitereg['mapred-queue-acls'],
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


        ## use encoding?
        encoding = None

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
                if dest2blackregcomp.has_key(dest) and any([r.search(k) for r in dest2blackregcomp[dest]]):
                    ## found in blacklist. skip it.
                    continue
                if dest2whiteregcomp.has_key(dest) and any([r.search(k) for r in dest2whiteregcomp[dest]]):
                    if not fullDict.has_key(dest):
                        fullDict[dest] = []
                    fullDict[dest].append(k)
            ## if not in any of the matched values, add to default
            if not any([k in v for v in fullDict.values()]):
                if not fullDict.has_key(defaultdestination):
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
            doc.writexml(sitefile, indent=" "*0, addindent=" "*0, newl="\n"*0)
            sitefile.close()

    def make_cfg(self):
        """Make the cfg file"""
        self.log.debug("make_cfg Making the config files")
        self.set_defaults()  ## set the default on missing values in params
        self.check_params() ## sanity check
        self.gen_conf_xml_new() ## write xml files

