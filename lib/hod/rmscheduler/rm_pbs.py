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
Implementation of the pbs resource manager

@author: Stijn De Weirdt
"""
from vsc import fancylogger


import os
import re

from hod.rmscheduler.resourcemanagerscheduler import ResourceManagerScheduler


class Pbs(ResourceManagerScheduler):
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
            self.pbsconn = pbs.pbs_connect(self.pbs_server)

        except ImportError:
            self.log.error("Cannot import PBSQuery or pbs. Please make sure pbs_python is installed and usable.")

        self.vars = {
            'cwd': 'PBS_O_WORKDIR',
            'jobid': 'PBS_JOBID',
        }

        self.jobid = None

    def submit(self, txt):
        """Submit the jobscript txt, set self.jobid"""
        self.log.debug("Going to submit script %s" % txt)

        attropl = pbs.new_attropl(2)  # jobparams
        attropl[0].name = 'Job_Name'
        attropl[0].value = self.options.get('name', 'python_pbs_job')
        attropl[1].name = 'Rerunable'
        attropl[1].value = 'y'

        for arg in self.args.keys():
            tmp = self.args[arg]
            tmpattropl = pbs.new_attropl(len(tmp))  # jobparams
            if arg in ('resources',):
                idx = 0
                for k, v in tmp.items():
                    tmpattropl[idx].name = 'Resource_List'  # resources
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
        tmpattropl[0].value = ",".join(["PBS_O_%s=%s" % (
            x, os.environ.get(x, 'NOTFOUND_%s' % x)) for x in defvars])
        attropl.extend(tmpattropl)

        import tempfile
        fh, scriptfn = tempfile.mkstemp()
        f = os.fdopen(fh, 'w')
        self.log.debug("Writing temp jobscript to %s" % scriptfn)
        f.write(txt)
        f.close()

        queue = self.args.get(
            'queue', self.options.get('queue', ''))  # do not set with attropl
        if queue:
            self.log.debug("Going to submit to queue %s" % queue)
        else:
            self.log.debug("No queue specified. Will submit to default destination.")

        extend = 'NULL'  # always
        jobid = pbs.pbs_submit(self.pbsconn, attropl, scriptfn, queue, extend)

        is_error, errormsg = pbs.error()
        if is_error:
            self.log.error("Failed to submit job script %s: error %s" %
                           (scriptfn, errormsg))
        else:
            self.log.debug("Succesful jobsubmission returned jobid %s" % jobid)
            self.jobid = jobid
            os.remove(scriptfn)

    def state(self, jobid=None, job_filter=None):
        """Return the state of job with id jobid"""
        if jobid is None:
            jobid = self.jobid

        state = self.info(
            jobid, types=['job_state', 'exec_host'], job_filter=job_filter)

        jid = [x['id'] for x in state]

        jstate = [x.get('job_state', None) for x in state]

        def get_uniq_hosts(txt, num=-1):
            """txt host1/cpuid+host2/cpuid
                - num: number of nodes to return
            """
            res = []
            for h_c in txt.split('+'):
                h = h_c.split('/')[0]
                if h in res:
                    continue
                res.append(h)
            return res[:num]
        ehosts = [get_uniq_hosts(x.get('exec_host', '')) for x in state]

        self.log.debug("Jobid  %s jid %s state %s ehosts %s (%s)" %
                       (jobid, jid, jstate, ehosts, state))

        joined = zip(jid, jstate, [''.join(x[:1]) for x in ehosts])  # only use first node (don't use [0], job in Q have empty list; use ''.join to make string)
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
            res = [dict([(typ, None) for typ in types + ['id']])]  # add id
            res = []  # return nothing
            self.log.debug("No job found. Wrong id %s or job finished? Returning %s" % (jobid, res))
            return res
        elif len(jobs) == 1:
            self.log.debug(
                "Request for jobid %s returned one result %s" % (jobid, jobs))
        else:
            self.log.error("Request for jobid %s returned more then one result %s" % (jobid, jobs))

        ## more then one, return value
        res = []
        for j in jobs:
            job_details = dict(
                [(attrib.name, attrib.value) for attrib in j.attribs])
            job_details['id'] = j.name  # add id
            if self.match_filter(job_details, job_filter):
                res.append(job_details)
        self.log.debug("Found jobinfo %s" % res)
        return res

    def match_filter(self, job, filter=None):
        """Apply filter to job"""
        if not filter:
            return True

        if 'Job_Name' in filter:
            ## name filter is regexp
            reg = re.compile(filter['Job_Name'])
            if reg.search(job['Job_Name']):
                return True

        return False

    def remove(self, jobid=None):
        """Remove the job with id jobid"""
        if jobid is None:
            jobid = self.jobid

        result = pbs.pbs_deljob(self.pbsconn, self.jobid, '')  # use empty string, not NULL (one can pass the deldelay=nnnn option)
        if result:
            self.log.error(
                "Failed to delete job %s: error %s" % (jobid, result))
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
            ppn = self.get_ppn(
            )  # hardcode for now TODO scan for min or max ppn per node
        elif ppn is None:
            ppn = 1

        walltime = int(float(walltime) * 60 * 60)  # in hours
        m, s = divmod(walltime, 60)
        h, m = divmod(m, 60)
        #d, h = divmod(h, 24) ## no days
        ## also prints leading 0s (do not insert if x > 0 (eg print 1:0)!
        # walltimetxt = ":".join(["%02d" % x for x in [ d,h, m, s]]) ## no days
        walltimetxt = ":".join(["%02d" % x for x in [h, m, s]])

        self.log.debug("Going to generate for nodes %s, ppn %s, walltime %s" %
                       (nodes, ppn, walltimetxt))

        self.args = {'resources': {'walltime': walltimetxt,
                                   'nodes': '%d:ppn=%d' % (nodes, ppn)
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
        for arg in self.args.keys():
            if arg in ('resources',):
                for k, v in self.args[arg].items():
                    opts.append("-l %s=%s" % (k, v))
            elif arg in ('mail',):
                opts.append('-m %s' % self.args[arg]['send'])
                if 'others' in self.args[arg]:
                    opts.append('-M %s' % self.args[arg]['others'])
            elif arg in ('queue',):
                if self.args[arg]:
                    opts.append('-q %s' % self.args[arg])
            else:
                self.log.debug("Unknown arg %s. Not adding to args." % arg)

        hdr = ['## Not actually used. pbs_submit bypasses submit filter.']
        hdr += ["#PBS %s" % x for x in opts]
        self.log.debug(
            "Created header %s (although not used by pbs_submit)" % hdr)
        return hdr

    def get_ppn(self):
        """Guess the ppn for full node"""
        pq = PBSQuery()
        node_vals = pq.getnodes().values()  # only the values, not the names
        interesni_nodes = ('free', 'job-exclusive',)
        res = {}
        for np in [int(x['np'][0]) for x in node_vals if x['state'][0] in interesni_nodes]:
            res.setdefault(np, 0)
            res[np] += 1

        ## return most frequent
        freq_count, freq_np = max([(j, i) for i, j in res.items()])
        self.log.debug("Found most frequent np %s (%s times) in interesni nodes %s" % (freq_np, freq_count, interesni_nodes))

        return freq_np
