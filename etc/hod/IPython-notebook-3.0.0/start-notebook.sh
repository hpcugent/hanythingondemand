#!/bin/bash
module load IPython/3.0.0-intel-2015a-Python-2.7.9
module load Python/2.7.9-intel-2015a
module load matplotlib/1.4.3-intel-2015a-Python-2.7.9
module load Spark/1.3.0

ipython profile create nbserver

config_dir=(mktmp -d ipython_notebook)

cat <<EOF > ${config_dir}/ipython_notebook_config.py
c = get_config()

# Kernel config
c.IPKernelApp.pylab = 'inline'  # if you want plotting support always

# Notebook config
c.NotebookApp.open_browser = False
#c.NotebookApp.password = u'sha1:bcd259ccf...[your hashed password here]'
# It is a good idea to put it on a known, fixed port
c.NotebookApp.port = 9999

EOF

# Add the PySpark classes to the Python path (taken from pyspark script):
export SPARK_HOME=$EBROOTSPARK
export PYTHONPATH="$SPARK_HOME/python/:$PYTHONPATH"
export PYTHONPATH="$SPARK_HOME/python/lib/py4j-0.8.2.1-src.zip:$PYTHONPATH"

export PYTHONPATH=$PYTHONPATH:$EBROOTPYTHON/lib/python2.7/site-packages/ 

ipython notebook --profile-dir=${config_dir}
