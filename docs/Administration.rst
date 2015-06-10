####################################
hanythingondemand for Administrators
####################################

This is a page for Administrators who wish to offer `hanythingondemand` on their PBS/Torque cluster. hanythingondemand is a particularly tricky project as it integrates several pieces of tecchnology (Torque, MPI, Java, Hadoop, on Python) and as such we don't have an out of the box installation procedure yet.

=============
Prerequisites
=============

Here's an overview of the dependencies:

* A cluster using `Torque <http://www.adaptivecomputing.com/products/open-source/torque/>`_
* `environment-modules <http://modules.sourceforge.net/>`_ (used to test HOD) to manage the environment
* `Python` - 2.7.*
* `Easybuild <https://github.com/hpcugent/easybuild>`_ - we use Easybuild for installing software and hanythingondemand isn't tested without it.
* `mpi4py <http://mpi4py.scipy.org/>`_
* `vsc-base <https://github.com/hpcugent/vsc-base>`_ - Used for command line parsing.
* `vsc-mympirun <https://github.com/hpcugent/vsc-mympirun>`_ - Used for setting up the MPI job.
* `pbs_python <https://oss.trac.surfsara.nl/pbs_python>`_ - Used for interacting with the PBS (aka Torque) server.
* `Netifaces <https://pypi.python.org/pypi/netifaces>`_
* `Netaddr <https://pypi.python.org/pypi/netaddr>`_
* `Java` 
* `Hadoop binaries <http://archive.cloudera.com/cdh4/cdh/4/>`_

======
Torque
======
To use hanythingondemand you must be running a cluster that uses `Torque <http://www.adaptivecomputing.com/products/open-source/torque/>`_ as the resource manager.

===================
Environment Modules
===================
We use `environment modules <http://modules.sourceforge.net/>`_ in conjunction with EasyBuild. You do not require environment-modules, however you will need to sort out all the paths for your users if you elect to not use it.

---------
Easybuild
---------
The following dependencies are installable using `Easybuild <https://github.com/hpcugent/easybuild>`_. They should be pulled in when using the ``eb hanythingondemand-${VERSION}.eb --robot`` command:

------
mpi4py
------
EasyBuild scripts for mpi4py are available `here <https://github.com/hpcugent/easybuild-easyconfigs/tree/master/easybuild/easyconfigs/m/mpi4py>`_

--------
vsc-base
--------
EasyBuild scripts for mpi4py are available `here <https://github.com/hpcugent/easybuild-easyconfigs/tree/master/easybuild/easyconfigs/v/vsc-base>`_

------------
vsc-mympirun
------------
EasyBuild scripts for mpi4py are available `here <https://github.com/hpcugent/easybuild-easyconfigs/tree/master/easybuild/easyconfigs/v/vsc-mympirun>`_

---------
netifaces
---------

EasyBuild scripts for mpi4py are available `here <https://github.com/hpcugent/easybuild-easyconfigs/tree/master/easybuild/easyconfigs/n/netifaces>`_

-------
netaddr
-------
EasyBuild scripts for mpi4py are available `here <https://github.com/hpcugent/easybuild-easyconfigs/tree/master/easybuild/easyconfigs/n/netaddr>`_

----------
pbs_python
----------
EasyBuild scripts for mpi4py are available `here <https://github.com/hpcugent/easybuild-easyconfigs/tree/master/easybuild/easyconfigs/p/pbs_python>`_

-----
Java
-----
We use the Oracle JVM which isn't directly installable from EasyBuild since you need to register on the website to get the files.

------
Hadoop
------
We use Cloudera's Hadoop distribution and have tested with chd4.4.0.

