#!/bin/bash

## on FC16, yum install mpi4py-mpich2

module load mpich2-x86_64

NP=4 

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

mpirun -np $NP python $HODPYTHONPATH/hod/hodproc.py
