#!/bin/bash

#PBS -l nodes=5:ppn=8
#PBS -l walltime=72:00:00

## on FC16, yum install mpi4py-mpich2

module load Python
module load Hadoop
module unload Java
module load Java/1.7.0_3

cd $PBS_O_WORKDIR


HODPYTHONPATH=$PWD/../../
if [ ! -d $HODPYTHONPATH/vsc ]
then
  echo "Add symlink from ln -s /usr/lib/python2.4/site-packages/vsc  $HODPYTHONPATH/vsc"
  exit 1
fi


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



# yarn
#export PATH=$HOME/hadoop/cdh4b1/hadoop-0.23.0-cdh4b1/bin:$PATH
# MR1

output=$PWD/hod.log.$PBS_JOBID

## use java opts for jdk7 for sdp
#export LD_PRELOAD=libsdp.so




mympirun --output=$output --variablesprefix=HADOOP,JAVA,HOD,YARN,HBASE,MAPRED,HDFS --hybrid=1 python $HODPYTHONPATH/hod/hodproc.py
