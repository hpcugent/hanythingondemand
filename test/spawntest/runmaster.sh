#!/bin/bash

## on FC16, yum install mpi4py-mpich2


module load mpich2-x86_64

mpirun -np 1 python master.py
