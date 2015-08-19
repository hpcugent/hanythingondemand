=====
Spark
=====
Many traditional HPC users who are interested in `Hadoop` are also very
interested in `Spark <http://spark.apache.org/>`_. With the claimed performance
improvements, it's easy to see why.

Spark works with Yarn out of the box so there's nothing special that needs to
happen with Hanythingondemand. Just use ``spark-submit --master=yarn-cluster``
with `all the other arguments to spark-submit
<https://spark.apache.org/docs/1.0.0/submitting-applications.html>`_, and it
works.
