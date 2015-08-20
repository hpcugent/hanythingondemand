#!/bin/bash

# exit as soon as an error occurs
set -e

module load IPython/3.2.1-intel-2015a-Python-2.7.10
module load matplotlib/1.4.3-intel-2015a-Python-2.7.10
module load Spark/1.4.1

ipython profile create nbserver

config_dir=(mktmp -d ipython_notebook)

cat <<EOF > ${config_dir}/ipython_notebook_config.py
c = get_config()

# Kernel config
c.IPKernelApp.pylab = 'inline'  # if you want plotting support always

# Notebook config
c.NotebookApp.open_browser = False
# It is a good idea to put it on a known, fixed port
c.NotebookApp.port = 8888
# use IPython.lib.passwd('password') to obtain the password hash
#c.NotebookApp.password = u'sha1:bcd259ccf...[your hashed password here]'

EOF

# Add the PySpark classes to the Python path (partially taken from pyspark script):
export PYTHONPATH="$EBROOTSPARK/python/:$EBROOTSPARK:python/lib/py4j-0.8.2.1-src.zip:$PYTHONPATH"

export PYTHONPATH=$PYTHONPATH:$EBROOTPYTHON/lib/python2.7/site-packages/ 

ipython notebook --profile-dir=${config_dir}
