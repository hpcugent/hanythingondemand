#!/bin/bash

## on FC16, yum install mpi4py-mpich2

#module load mpich2-x86_64

## run 1 process per node to start local cluster
NP=${NPP:-1}

basedir=`dirname $(readlink -m $0)`
HODPYTHONPATH=$basedir/../../lib/

if [ ! -d $HODPYTHONPATH/hod ]
then
    echo "hod not found in HODPYTHONPATH $HODPYTHONPATH"
    exit 1
fi


if [ -z $PYTHONPATH ]
then
    export PYTHONPATH=$HODPYTHONPATH
else
    export PYTHONPATH=$HODPYTHONPATH:$PYTHONPATH
fi

export JAVA_HOME=/usr/lib/jvm/java

# yarn
#export PATH=$HOME/hadoop/cdh4b1/hadoop-0.23.0-cdh4b1/bin:$PATH
# MR1
export PATH=$HOME/hadoop/cdh3u3/hadoop-0.20.2-cdh3u3/bin:$PATH


mpirun -np $NP python $HODPYTHONPATH/hod/hodproc.py
echo done
