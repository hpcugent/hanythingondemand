#!/bin/bash

## on FC16, yum install mpi4py-mpich2

module load mpich2-x86_64

NP=4 

mpirun -np $NP python sample.py
