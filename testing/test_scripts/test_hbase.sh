#!/bin/bash

time hbase org.apache.hadoop.hbase.PerformanceEvaluation randomWrite 4
time hbase org.apache.hadoop.hbase.PerformanceEvaluation randomRead 4
