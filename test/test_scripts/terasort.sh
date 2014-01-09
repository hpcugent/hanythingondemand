#!/bin/bash
## easybuild preloaded (SOFTROOTHADOOP is HADOOP_HOME)
hadoop fs -mkdir /benchmarks

## generate input of rows *1M * 100byte rows (=100MB * rows)
rows=10 ## sample 1GB
time hadoop jar $SOFTROOTHADOOP/hadoop-*examples*.jar teragen $(($rows*1000*1000)) /benchmarks/teragen
hadoop dfsadmin -report
time hadoop jar $SOFTROOTHADOOP/hadoop-*examples*.jar terasort /benchmarks/teragen /benchmarks/teragen-out
hadoop dfsadmin -report
hadoop jar $SOFTROOTHADOOP/hadoop-*examples*.jar teravalidate /benchmarks/teragen-out /benchmarks/teragen-val
hadoop fs -rmr /benchmarks/teragen /benchmarks/teragen-out /benchmarks/teragen-val

