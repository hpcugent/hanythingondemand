#!/bin/bash

## on FC16, yum install mpi4py-mpich2

module load mpich2-x86_64

NP=${NPP:-4} 

basedir=`dirname $(readlink -m $0)`
HODPYTHONPATH=$basedir/../../

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
export PATH=/home/stdweird/hadoop/cdh4b1/hadoop-0.23.0-cdh4b1/bin:$PATH

mpirun -np $NP python $HODPYTHONPATH/hod/hodproc.py
