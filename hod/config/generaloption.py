
#
# Copyright 2012 Stijn De Weirdt
# 
# This file is part of HanythingOnDemand,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
from vsc import fancylogger


from optparse import OptionParser, OptionGroup, Option, make_option
import sys, re

extra_options = ("extend",)

class ExtOption(Option):
    """Extended options class"""

    ACTIONS = Option.ACTIONS + extra_options
    STORE_ACTIONS = Option.STORE_ACTIONS + extra_options
    TYPED_ACTIONS = Option.TYPED_ACTIONS + extra_options
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + extra_options

    def take_action(self, action, dest, opt, value, values, parser):
        if action in extra_options:
            if action == "extend":
                lvalue = value.split(",")
                values.ensure_value(dest, []).extend(lvalue)
            else:
                raise("Unknown extended option action %s (known: %s)" % (action, extra_options))
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)

class ExtOptionParser(OptionParser):
    """Make an option parser that limits the -h to short opts only"""
    def print_help(self, fn=None):
        OptionParser.print_help(self, fn)


OPTNAME_SEPARATOR = '_'

debug_options_build = False

class GeneralOption:
    """Simple wrapper class for optiopn parsing"""
    def __init__(self):
        self.parser = ExtOptionParser(option_class=ExtOption)

        self.log = fancylogger.getLogger(self.__class__.__name__)
        self.options = None
        self.processed_options = {}


        self.set_debug()

        self.make_debug_options()

        self.make_init()

        self.parseoptions()

        self.set_debug()

    def set_debug(self):
        """Check if debug options are on and then set fancylogger to debug"""
        if self.options is None:
            if debug_options_build:
                fancylogger.setLogLevelDebug()  ## debug mode when building the options ?
        else:
            if self.options.debug:
                fancylogger.setLogLevelDebug()


    def make_debug_options(self):
        """Add debug option"""
        opts = {'debug':("Enable debug mode (default %default)", None, "store_true", False, 'd')
                }
        descr = ['Debug options', '']
        self.log.debug("Add debug options descr %s opts %s (no prefix)" % (descr, opts))
        self.add_group_parser(opts, descr, prefix=None)

    def make_init(self):
        """Trigger all inits"""
        self.log.error("Not implemented")

    def add_group_parser(self, opt_dict, description, prefix=None):
        """Make a group parser from a dict
            - key: long opt --prefix.key
            - value: tuple (help,type,action,default(,optional short option))
            -- help will be extended with type and default
          Description is a 2 element list (short and long description)
        """
        opt_grp = OptionGroup(self.parser, description[0], description[1])
        keys = opt_dict.keys()
        keys.sort() ## alphabetical
        for key in keys:
            details = opt_dict[key]

            hlp = details[0]
            typ = details[1]
            action = details[2]
            default = details[3]

            extra_help = []
            if action in ("extend",):
                extra_help.append("type comma-seperated list")
            elif typ is not None:
                extra_help.append("type %s" % typ)

            if default is not None:
                extra_help.append("def %s" % default)

            if extra_help:
                hlp += " (%s)" % (";".join(extra_help))

            if prefix:
                dest = "%s%s%s" % (prefix, OPTNAME_SEPARATOR, key)
            else:
                dest = "%s" % key

            self.processed_options[dest] = [typ, default, action] ## add longopt


            nameds = {'dest':dest, 'help':hlp, 'action':action, 'metavar':key.upper()}
            if default:
                nameds['default'] = default

            if typ:
                nameds['type'] = typ

            args = ["--%s" % dest]
            try:
                shortopt = details[4]
                args.insert(0, "-%s" % shortopt)
            except IndexError:
                shortopt = None

            opt_grp.add_option(*args, **nameds)
        self.parser.add_option_group(opt_grp)


    def parseoptions(self, optionsstring=sys.argv[1:]):
        """parse the options"""
        (self.options, args) = self.parser.parse_args(optionsstring)
        #args should be empty, since everything is optional
        if len(args) > 1:
            self.parser.error("Invalid arguments args %s" % args)

        self.log.debug("Found options %s" % self.options)

    def dict_by_prefix(self):
        """Break the options dict by prefix in sub-dict"""
        subdict = {}
        for k in self.options.__dict__.keys():
            levels = k.split(OPTNAME_SEPARATOR)
            lastlvl = subdict
            for lvl in levels[:-1]: ## 0 or more
                lastlvl.setdefault(lvl, {})
                lastlvl = lastlvl[lvl]
            lastlvl[levels[-1]] = self.options.__dict__[k]
        self.log.debug("Returned subdict %s" % subdict)
        return subdict

    def generate_cmd_line(self, ignore=None):
        """Create the commandline options that would create the current self.options
            - this assumes that optname is longopt!
        """
        if ignore:
            self.log.debug("generate_cmd_line ignore %s" % ignore)
            ignore = re.compile(ignore)
        else:
            self.log.debug("generate_cmd_line no ignore")

        args = []
        opt_names = self.options.__dict__.keys()
        opt_names.sort()

        for opt_name in opt_names:
            opt_value = self.options.__dict__[opt_name]
            if ignore and ignore.search(opt_name):
                self.log.debug("generate_cmd_line adding %s value %s matches ignore. not adding to args." % (opt_name, opt_value))
                continue

            typ, default, action = self.processed_options[opt_name]
            if opt_value == default:
                ## do nothing
                self.log.debug("generate_cmd_line adding %s value %s default found. not adding to args." % (opt_name, opt_value))
                continue
            elif opt_value is None:
                ## do nothing
                self.log.debug("generate_cmd_line adding %s value %s. None found. not adding to args." % (opt_name, opt_value))
                continue

            if action in ("store_true", "store_false",):
                ## not default!
                self.log.debug("generate_cmd_line adding %s value %s. store action found" % (opt_name, opt_value))
                args.append("--%s" % opt_name)
            elif action in ("extend",):
                ## comma separated
                self.log.debug("generate_cmd_line adding %s value %s. extend action, return as comma-separated list" % (opt_name, opt_value))
                args.append("--%s=%s" % (opt_name, ",".join(opt_value)))
            elif action in ("append",):
                ## add multiple times
                self.log.debug("generate_cmd_line adding %s value %s. append action, return as multiple args" % (opt_name, opt_value))
                for v in opt_value:
                    args.append("--%s='%s'" % (opt_name, v))
            else:
                self.log.debug("generate_cmd_line adding %s value %s" % (opt_name, opt_value))
                args.append("--%s='%s'" % (opt_name, opt_value))

        self.log.debug("commandline args %s" % args)
        return args

