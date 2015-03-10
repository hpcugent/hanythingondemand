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
