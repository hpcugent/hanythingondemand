#!/bin/bash

# exit as soon as an error occurs
set -e

# This requires IPython, matplotlib, and Spark to be loaded. These are set in
# the hod.conf file.

ipython profile create nbserver

if [[ ! -d "$1" ]] ; then
    echo "Argument <localworkdir> required" 
    exit 1
fi

config_dir="$1/conf/ipython_notebook"
log_dir="$1/log"

mkdir -p "$config_dir"
mkdir -p "$log_dir"

cat <<EOF > "${config_dir}/ipython_notebook_config.py"
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
export PYTHONPATH="$EBROOTSPARK/python/:$EBROOTSPARK/python/lib/py4j-0.9-src.zip:$PYTHONPATH"

export PYTHONPATH=$PYTHONPATH:$EBROOTPYTHON/lib/python2.7/site-packages/ 

# Start IPython notebook through pyspark's scripts.
export PYSPARK_DRIVER_PYTHON=ipython 
export PYSPARK_DRIVER_PYTHON_OPTS="notebook --profile-dir=${config_dir}" 
export PYSPARK_SUBMIT_ARGS="--master yarn --deploy-mode client"
nohup pyspark --master yarn >"$log_dir/pyspark.stdout" 2>"$log_dir/pyspark.stderr" &
