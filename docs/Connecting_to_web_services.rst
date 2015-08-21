.. _connecting_to_web_uis:

Connecting to web user interfaces
=================================

To connect to web user interfaces that are available for a running HOD cluster, you need to follows these steps:

1. Set up an SSH tunnel to the head node of your HOD cluster (see :ref:`setting_up_ssh_tunnel`)
2. Configure your browser to use the SSH tunnel as a SOCKS proxy (see :ref:`browser_proxy_configuration`)
3. Point your browser to ``http://localhost:<port>`` (see :ref:`web_ui_ports`)

.. contents::
    :depth: 3
    :backlinks: none

.. _setting_up_ssh_tunnel:

Setting up an SSH tunnel
------------------------

.. _setting_up_ssh_tunnel_linux_osx:

Setting up an SSH tunnel in Linux/Mac OS X
******************************************


.. _setting_up_ssh_tunnel_windows:

Setting up an SSH tunnel in Windows using PuTTy
***********************************************

http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html


.. _browser_proxy_configuration:

Browser SOCKS proxy configuration
---------------------------------

.. _browser_proxy_configuration_chrome:

Chrome SOCKS proxy configuration
********************************

.. _browser_proxy_configuration_firefox:

Firefox SOCKS proxy configuration
*********************************

.. _browser_proxy_configuration_ie:

Internet Explorer SOCKS proxy configuration
*******************************************

.. _browser_proxy_configuration_safari:

Safari SOCKS proxy configuration
********************************


.. _web_ui_ports:

Ports for web user interfaces
-----------------------------

Once you have set up an SSH tunnel (see :ref:`setting_up_ssh_tunnel`) and have configured your browsers to use it as
a SOCKS proxy (see :ref:`browser_proxy_configuration`), you can connect to the web user interfaces available in your
running HOD cluster via::

    http://localhost:<port>

The port number to use depends on the particular web user interface you want to connect to, see below.

.. _web_ui_ports_hadoop:

Ports for Hadoop web user interface (defaults)
**********************************************

* ``50030``: Hadoop job tracker
* ``50060``: Hadoop task tracker

* ``50070``: HFDS name node
* ``50075``: HDFS data nodes
* ``50090``: HDFS secondary name node
* ``50105``: HDFS backup/checkpoint node

(see also http://blog.cloudera.com/blog/2009/08/hadoop-default-ports-quick-reference)

.. _web_ui_ports_ipython:

Ports for IPython web services
******************************

* ``8888``: IPython notebook
