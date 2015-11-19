XML_PREAMBLE = """<?xml version="1.0" encoding="utf-8"?>
"""

HADOOP_STYLESHEET = """<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
"""

def kv2xml(name, value):
    """Take a config option and return an xml string"""
    return '''<property>
    <name>%s</name>
    <value>%s</value>
</property>
''' % (name, value)

def write_whitespace_delimited_file(_, options, template_resolver):
    """
    Write a whitespace delimited file. e.g.:

    property1 value1
    property2 value2

    "spark-defaults.conf" is one such example:
    https://spark.apache.org/docs/latest/configuration.html#dynamically-loading-spark-properties
    """
    output = ""

    for key, val in sorted(options.items()):
        name = template_resolver(key)
        value = template_resolver(val)
        output += '%s %s\n' % (name, value)
    return output
