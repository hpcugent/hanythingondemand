#!/usr/bin/env python

"""
Generate a PBS job script using pbs_python. Will use mympirun to get the all started
"""

from vsc import fancylogger
fancylogger.setLogLevelDebug()

import os, sys, re

class ResourceManagerscheduler:
    """Class to implement"""
    def __init__(self):
        self.log = fancylogger.getLogger(self.__class__.__name__)

        self.vars = {'cwd':None,
                     'jobid':None,
                     }
        self.jobid = None

        self.job_filter = None

    def submit(self, txt):
        """Submit the jobscript txt, set self.jobid"""
        self.log.error("submit not implemented")

    def state(self, jobid=None):
        """Return the state of job with id jobid"""
        if jobid is None:
            jobid = self.jobid
        self.log.error("state not implemented")

    def remove(self, jobid=None):
        """Remove the job with id jobid"""
        if jobid is None:
            jobid = self.jobid
        self.log.error("remove not implemented")

    def header(self, nodes=5, ppn= -1, walltime=72):
        """Return the script header that requests the properties.
           nodes = number of nodes
           ppn = ppn (-1 = full node)
           walltime = time in hours (can be float)
        """
        self.log.error("header not implemented")


class Pbs(ResourceManagerscheduler):
    """Interaction with torque"""
    def __init__(self, options):
        self.log = fancylogger.getLogger(self.__class__.__name__)
        self.options = options
        self.log.debug("Provided options %s" % options)

        global PBSQuery
        global pbs
        try:
            from PBSQuery import PBSQuery
            import pbs

            self.pbs_server = pbs.pbs_default()
            self.pbsconn = pbs.pbs_connect (self.pbs_server)

        except ImportError:
            self.log.error("Cannot import PBSQuery")



        self.vars = {'cwd':'PBS_O_WORKDIR',
                     'jobid':'PBS_JOBID',
                     }

        self.jobid = None


    def submit(self, txt):
        """Submit the jobscript txt, set self.jobid"""
        self.log.debug("Going to submit script %s" % txt)



        attropl = pbs.new_attropl(2) ## jobparams
        attropl[0].name = 'Job_Name'
        attropl[0].value = self.options.get('name', 'python_pbs_job')
        attropl[1].name = 'Rerunable'
        attropl[1].value = 'y'

        for arg in self.args.keys():
            tmp = self.args[arg]
            tmpattropl = pbs.new_attropl(len(tmp)) ## jobparams
            if arg in ('resources',):
                idx = 0
                for k, v in tmp.items():
                    tmpattropl[idx].name = 'Resource_List' ## resources
                    tmpattropl[idx].resource = k
                    tmpattropl[idx].value = v
                    idx += 1
            elif arg in ('mail',):
                tmpattropl[0].name = 'Mail_Points'
                tmpattropl[0].value = tmp['send']
                if len(tmp) > 1:
                    tmpattropl[0].name = "Mail_Users"
                    tmpattropl[0].value = tmp['others']
            elif arg in ('queue',):
                ## use destination field of pbs_submit
                pass
            else:
                self.log.error('Unknown arg %s' % arg)
                tmpattropl = pbs.new_attropl(0)

            attropl.extend(tmpattropl)

        ## add a bunch of variables (added by qsub)
        ## also set PBS_O_WORKDIR to os.getcwd()
        os.environ.setdefault('WORKDIR', os.getcwd())

        defvars = ['MAIL', 'HOME', 'PATH', 'SHELL', 'WORKDIR']

        tmpattropl = pbs.new_attropl(1)
        tmpattropl[0].name = 'Variable_List'
        tmpattropl[0].value = ",".join([ "PBS_O_%s=%s" % (x, os.environ.get(x, 'NOTFOUND_%s' % x)) for x in defvars ])
        attropl.extend(tmpattropl)


        import tempfile
        fh, scriptfn = tempfile.mkstemp()
        f = os.fdopen(fh, 'w')
        self.log.debug("Writing temp jobscript to %s" % scriptfn)
        f.write(txt)
        f.close()

        queue = self.args.get('queue', self.options.get('queue', '')) ## do not set with attropl
        if queue:
            self.log.debug("Going to submit to queue %s" % queue)
        else:
            self.log.debug("No queue specified. Will submit to default destination.")

        extend = 'NULL' ## always
        jobid = pbs.pbs_submit(self.pbsconn, attropl, scriptfn, queue, extend)

        is_error, errormsg = pbs.error()
        if is_error:
            self.log.error("Failed to submit job script %s: error %s" % (scriptfn, errormsg))
        else:
            self.log.debug("Succesful jobsubmission returned jobid %s" % jobid)
            self.jobid = jobid
            os.remove(scriptfn)

    def state(self, jobid=None, job_filter=None):
        """Return the state of job with id jobid"""
        if jobid is None:
            jobid = self.jobid

        state = self.info(jobid, types=['job_state', 'exec_host'], job_filter=job_filter)

        jid = [x['id'] for x in state]

        jstate = [ x.get('job_state', None) for x in state]

        def get_uniq_hosts(txt, num= -1):
            """txt host1/cpuid+host2/cpuid
                - num: number of nodes to return
            """
            res = []
            for h_c in txt.split('+'):
                h = h_c.split('/')[0]
                if h in res: continue
                res.append(h)
            return res[:num]
        ehosts = [ get_uniq_hosts(x.get('exec_host', '')) for x in state]

        self.log.debug("Jobid  %s jid %s state %s ehosts %s (%s)" % (jobid, jid, jstate, ehosts, state))

        joined = zip(jid, jstate, [''.join(x[:1]) for x in ehosts]) ## only use first node (don't use [0], job in Q have empty list; use ''.join to make string)
        temp = "Id %s State %s Node %s"
        if len(joined) == 0:
            msg = "No jobs found."
        elif len(joined) == 1:
            msg = "Found 1 job %s" % (temp % tuple(joined[0]))
        else:
            msg = "Found %s jobs\n" % len(joined)
            for j in joined:
                msg += "    %s\n" % (temp % tuple(j))
        self.log.debug("msg %s" % msg)

        return msg

    def info(self, jobid, types=None, job_filter=None):
        """Return jobinfo"""
        ## TODO restrict to current user jobs
        if type(types) is str:
            types = [types]
        self.log.debug("Return info types %s" % types)

        ## add all filter values to the types
        if job_filter is None:
            job_filter = {}
        self.log.debug("Job filter passed %s" % job_filter)
        if self.job_filter is not None:
            self.log.debug("Job filter update with %s" % self.job_filter)
            job_filter.update(self.job_filter)
        self.log.debug("Job filter used %s" % job_filter)

        for filter_name in job_filter.keys():
            if not filter_name in types:
                types.append(filter_name)

        if types is None:
            jobattr = 'NULL'
        else:
            jobattr = pbs.new_attrl(len(types))
            for idx in range(len(types)):
                jobattr[idx].name = types[idx]

        jobs = pbs.pbs_statjob(self.pbsconn, jobid, jobattr, 'NULL')
        if len(jobs) == 0:
            res = [dict([(typ, None) for typ in types + ['id']])]  ## add id
            res = [] ## return nothing
            self.log.debug("No job found. Wrong id %s or job finished? Returning %s" % (jobid, res))
            return res
        elif len(jobs) == 1:
            self.log.debug("Request for jobid %s returned one result %s" % (jobid, jobs))
        else:
            self.log.error("Request for jobid %s returned more then one result %s" % (jobid, jobs))


        ## more then one, return value
        res = []
        for j in jobs:
            job_details = dict([ (attrib.name, attrib.value) for attrib in j.attribs  ])
            job_details['id'] = j.name ## add id
            if self.match_filter(job_details, job_filter):
                res.append(job_details)
        self.log.debug("Found jobinfo %s" % res)
        return res

    def match_filter(self, job, filter=None):
        """Apply filter to job"""
        if not filter:
            return True

        if filter.has_key('Job_Name'):
            ## name filter is regexp
            reg = re.compile(filter['Job_Name'])
            if reg.search(job['Job_Name']):
                return True

        return False


    def remove(self, jobid=None):
        """Remove the job with id jobid"""
        if jobid is None:
            jobid = self.jobid

        result = pbs.pbs_deljob(self.pbsconn, self.jobid, '') ## use empty string, not NULL (one can pass the deldelay=nnnn option)
        if result:
            self.log.error("Failed to delete job %s: error %s" % (jobid, result))
        else:
            self.log.debug("Succesfully deleted job %s" % jobid)


    def header(self):
        """Return the script header that requests the properties.
           nodes = number of nodes
           ppn = ppn (-1 = full node)
           walltime = time in hours (can be float)
        """
        nodes = self.options.get('nodes', 50)
        ppn = self.options.get('ppn', -1)
        walltime = self.options.get('walltime', 72)
        mail = self.options.get('mail', [])
        mail_others = self.options.get('mailothers', [])
        queue = self.options.get('queue', 'default')

        self.log.debug("Arguments nodes %s, ppn %s, walltime %s, mail %s, mail_others %s, queue %s" % (nodes, ppn, walltime, mail, mail_others, queue))
        if nodes is None:
            nodes = 1

        if ppn == -1:
            ppn = self.get_ppn() ## hardcode for now TODO scan for min or max ppn per node
        elif ppn is None:
            ppn = 1

        walltime = int(float(walltime) * 60 * 60) ## in hours
        m, s = divmod(walltime, 60)
        h, m = divmod(m, 60)
        #d, h = divmod(h, 24) ## no days
        ## also prints leading 0s (do not insert if x > 0 (eg print 1:0)! 
        # walltimetxt = ":".join(["%02d" % x for x in [ d,h, m, s]]) ## no days
        walltimetxt = ":".join(["%02d" % x for x in [ h, m, s]])


        self.log.debug("Going to generate for nodes %s, ppn %s, walltime %s" % (nodes, ppn, walltimetxt))

        self.args = {'resources':{'walltime':walltimetxt,
                                  'nodes':'%d:ppn=%d' % (nodes, ppn)
                                  },
                     }

        if queue:
            self.args['queue'] = queue

        if mail or mail_others:
            self.args['mail'] = {}
            if not mail:
                mail = ['e']
            self.args['mail']['send'] = ''.join(mail)
            if mail_others:
                self.args['mail']['others'] = ','.join(mail_others)

        self.log.debug("Create args %s" % self.args)

        ## creating the header. Not used in submission!!
        opts = []
        for arg  in self.args.keys():
            if arg in ('resources',):
                for k, v in self.args[arg].items():
                    opts.append("-l %s=%s" % (k, v))
            elif arg in ('mail',):
                opts.append('-m %s' % self.args[arg]['send'])
                if self.args[arg].has_key('others'):
                    opts.append('-M %s' % self.args[arg]['others'])
            elif arg in ('queue',):
                if self.args[arg]:
                    opts.append('-q %s' % self.args[arg])
            else:
                self.log.debug("Unknown arg %s. Not adding to args." % arg)

        hdr = ['## Not actually used. pbs_submit bypasses submit filter.']
        hdr += ["#PBS %s" % x for x in opts]
        self.log.debug("Created header %s (although not used by pbs_submit)" % hdr)
        return hdr


    def get_ppn(self):
        """Guess the ppn for full node"""
        pq = PBSQuery()
        node_vals = pq.getnodes().values() ## only the values, not the names
        interesni_nodes = ('free', 'job-exclusive',)
        res = {}
        for np in [int(x['np'][0]) for x in node_vals if x['state'][0] in interesni_nodes]:
            res.setdefault(np, 0)
            res[np] += 1

        ## return most frequent
        freq_count, freq_np = max([(j, i) for i, j in res.items()])
        self.log.debug("Found most frequent np %s (%s times) in interesni nodes %s" % (freq_np, freq_count, interesni_nodes))

        return freq_np

class Job:
    def __init__(self, options):
        self.log = fancylogger.getLogger(self.__class__.__name__)

        self.options = options

        self.nrnodes = None
        self.corespernode = None

        self.script = None

        self.type = None

        self.modules = []

        self.run_in_cwd = True


    def submit(self):
        """Submit this job"""
        if self.script is None:
            self.generate_script()

        self.log.debug("Going to submit jobscript %s" % self.script)
        self.type.submit(self.script)
        self.log.debug("Submission returned jobid %s" % self.type.jobid)

    def generate_script(self):
        """Build the submit script"""
        script = ["#!/bin/bash", "## Generated by HOD"]
        script += self.generate_script_header()

        script += self.generate_modules()

        if self.run_in_cwd:
            script.append("cd $%s" % self.type.vars['cwd'])

        script += self.generate_exe()

        self.log.debug("Generated script %s" % script)
        self.script = "\n".join(script + [''])

    def generate_exe(self):
        """The actual executable"""
        self.log.debug("generate_exe not implemented")

        return ['## Not implemented']

    def generate_script_header(self):
        """Create the job arguments. Retrun as header (if used)"""
        hdr = self.type.header()
        self.log.debug("Generated header %s" % hdr)

        return hdr

    def generate_modules(self):
        """Generate the module statements. Returns a list. Elements that are string or 1 long are assumed to be load requests"""
        allmods = []
        for md in self.modules:
            if type(md) in (str,):
                allmods.append(['load', md])
            elif type(md) in (list, tuple):
                if len(md) == 1:
                    allmods.append(['load', md[0]])
                else:
                    allmods.append(md)
            else:
                self.log.error("Unknown module type %s (%s)" % (type(md), md))

        self.log.debug("Going to generate string for modules %s" % allmods)
        return ['module %s' % (" ".join(md)) for md in allmods]


class Hod(Job):
    """Hanything on demand job"""
    def __init__(self):
        from hod.config.options import HodOption
        options = HodOption()

        Job.__init__(self, options)

        self.exeout = None

        self.hodexe, self.hodpythonpath = self.get_hod()
        self.hodargs = self.options.generate_cmd_line(ignore='^(rm|action)_')

        self.hodenvvarprefix = ['HADOOP', 'JAVA', 'HOD', 'MAPRED', 'HDFS']
        if not self.options.options.hdfs_off:
            self.hodenvvarprefix.append('HDFS')
        if not self.options.options.mr1_off:
            self.hodenvvarprefix.append('MAPRED')
        if self.options.options.yarn_on:
            self.hodenvvarprefix.append('YARN')
        if self.options.options.hbase_on:
            self.hodenvvarprefix.append('HBASE')

        self.set_type_class()

        self.name_suffix = 'HOD' ## suffixed name, to lookup later
        options_dict = self.options.dict_by_prefix()
        options_dict['rm']['name'] = "%s_%s" % (options_dict['rm']['name'], self.name_suffix)
        self.type = self.type_class(options_dict['rm'])

        self.type.job_filter = {'Job_Name':'%s$' % self.name_suffix} ## all jobqueries are filter on this suffix

        self.run_in_cwd = True

        self.exeout = "$%s/hod.output.$%s" % (self.type.vars['cwd'], self.type.vars['jobid'])


    def set_type_class(self):
        """Set the typeclass"""
        self.log.debug("Using default class ResourceManagerscheduler.")
        self.type_class = ResourceManagerscheduler


    def get_hod(self, exe_name='hodproc.py'):
        """Get the full path of the exe_name
 -look in bin or bin / .. / hod /
        """
        fullscriptname = os.path.abspath(sys.argv[0])

        bindir = os.path.dirname(fullscriptname)
        hodpythondir = os.path.abspath("%s/.." % bindir)
        hoddir = os.path.abspath("%s/../hod" % bindir)

        self.log.debug("Found fullscriptname %s binname %s hoddir %s" % (fullscriptname, bindir, hoddir))

        fn = None
        paths = [bindir, hoddir]
        for tmpdir in paths:
            fn = os.path.join(tmpdir, exe_name)
            if os.path.isfile(fn):
                self.log.debug("Found exe_name %s location %s" % (exe_name, fn))
                break
            else:
                fn = None
        if not fn:
            self.log.error("No exe_name %s found in paths %s" % (exe_name, paths))

        return fn, hodpythondir

    def run(self):
        """Do stuff based upon options"""
        options_dict = self.options.dict_by_prefix()
        actions = options_dict['action']
        self.log.debug("Found actions %s" % actions)
        if actions.get('create', False):
            self.submit()
            msg = self.type.state()
            print msg
        elif actions.get('remove', None):
            self.type.remove()
        elif actions.get('show', None):
            msg = self.type.state()
            print msg
        elif actions.get('showall', False): ## should be True
            msg = self.type.state()
            print msg
        else:
            self.log.error("Unknown action in actions %s" % actions)

class UgentHod(Hod):
    """Hod type job for UGent HPC infrastructure
        - type PBS
        - mympirun cmd style
    """
    def __init__(self):
        Hod.__init__(self)

        self.modules = ['Python'] ## no version?

        self.modules.append('Hadoop/%s' % self.options.options.hadoop_module)

        if self.options.options.hbase_on:
            self.modules.append('HBase/%s' % self.options.options.hbase_module)

        if self.options.options.java_module:
            ## force Java module
            self.modules.append(['unload', 'Java'])
            self.modules.append('Java/%s' % self.options.options.java_module) ## TODO fixed version of 170_3


    def set_type_class(self):
        """Set the typeclass"""
        self.log.debug("Using default class Pbs.")
        self.type_class = Pbs

    def generate_exe(self):
        """Mympirun executable"""
        pythonenv = """HODPYTHONPATH=%s
if [ -z $PYTHONPATH ]
then
    export PYTHONPATH=$HODPYTHONPATH
else
    export PYTHONPATH=$HODPYTHONPATH:$PYTHONPATH
fi
""" % self.hodpythonpath

        exe = ["mympirun"]
        if self.exeout:
            exe.append("--output=%s" % self.exeout)
        exe.append("--hybrid=1")

        exe.append('--variablesprefix=%s' % ','.join(self.hodenvvarprefix))

        exe.append('python') ## TODO abs path?
        exe.append(self.hodexe)
        exe += self.hodargs

        self.log.debug("Generated exe %s" % exe)
        return [pythonenv, " ".join(exe)]


if __name__ == '__main__':
    """Create the job script and submit it"""
    j = UgentHod()
    j.run()
