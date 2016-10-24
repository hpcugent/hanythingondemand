.. _connecting_to_web_uis:

Connecting to web user interfaces
=================================

To connect to web user interfaces (UIs) that are available for a running HOD cluster, you need to follow these steps:

1. Set up an SSH tunnel to the head node of your HOD cluster (see :ref:`ssh_tunnel`)
2. Configure your browser to use the SSH tunnel as a SOCKS proxy (see :ref:`browser_proxy_configuration`)
3. Point your browser to ``http://localhost:<port>`` (see :ref:`web_ui_ports`)

.. contents::
    :depth: 3
    :backlinks: none

.. _ssh_tunnel:

Setting up an SSH tunnel
------------------------

To connect to a web UI available on your running `hanythingondemand` cluster, you most likely need to set up
an SSH tunnel first.

Typically, the HOD cluster is running on a workernode of an HPC cluster that is only accessible via the HPC login nodes.
To connect to a web UI however, we need *direct* access. This can be achieved by tunneling via SSH over the login nodes.

To set up an SSH tunnel, follow these steps:

1. Determine hostname of the head node of your HOD cluster (see :ref:`ssh_tunnel_hostname`)
2. Configure your SSH client (see :ref:`ssh_tunnel_client_configuration`)
3. Start the SSH tunnel (see :ref:`start_SSH_tunnel`)

.. _ssh_tunnel_hostname:

Determine hostname of head node of HOD cluster
**********************************************

The first step is to figure out which workernode is the *head* node of your HOD cluster, using ``hod list``.

For example::

    $ hod list
    Cluster label   Job ID                            State   Hosts                   
    example         123456.master15.delcatty.gent.vsc R       node2001.delcatty.gent.vsc

So, in this example, ``node2001.delcatty.gent.vsc`` is the `fully qualified domain name (FQDN)` of the head node
of our HOD cluster.

.. _ssh_tunnel_client_configuration:

Configuring your SSH client to use an SSH tunnel
************************************************

See the sections below how to configure your SSH client.

.. _ssh_tunnel_client_configuration_osx_linux:

Configuring SSH in Mac OS X or Linux
++++++++++++++++++++++++++++++++++++

To configure SSH to connect to a particular workernode using an SSH tunnel, you need to add a couple of lines to
your ``$HOME/.ssh/config`` file.

For example, to configure SSH that it should tunnel via the HPC login node ``login.hpc.ugent.be`` for all FQDNs
that start with ``node`` and end with ``.gent.vsc``, using ``vsc40000`` as a user name, the following lines should be added::

  Host login.hpc.ugent.be hpc
      Hostname login.hpc.ugent.be
      User vsc40000
      IdentityFile ~/.ssh/id_rsa

  Host node*.gent.vsc
      ProxyCommand ssh -q login.hpc.ugent.be 'exec nc -w 21600s %h %p'
      User vsc40000
      IdentityFile ~/.ssh/id_rsa

Make sure to point it to your ssh private key (``~/.ssh/id_rsa`` in this example). If you only have a single private key,
this line can be dropped.


.. _ssh_tunnel_client_configuration_windows:

Configuring PuTTY in Windows
++++++++++++++++++++++++++++

:ref:`configuring_putty_on_windows` is more involved than Linux or OS X so it has its own page.

.. _start_SSH_tunnel:

Starting the SSH tunnel
***********************

To start the SSH tunnel, simply set up an SSH connection to that head node of your HOD cluster, while specifying
a `local port` that can be used to set up a SOCKS proxy to that workernode.

You can choose a port number yourself, but stick to numbers **higher than 1024** (lower ports are priveledged ports,
and thus require adminstration rights).

We will use port number ``10000`` (`ten thousand`) as an example below (and you should be able to use it too).

.. _start_SSH_tunnel_osx_linux:

Starting the SSH tunnel on Mac OS X or Linux
++++++++++++++++++++++++++++++++++++++++++++

On OS X or Linux, just SSH to the FQDN of the head node of the HOD cluster, and specify the local port you want
to use for your SOCKS proxy via the ``-D`` option of the SSH command.

For example, to connect to ``node2001.delcatty.gent.vsc`` using port ``10000``::

    $ ssh -D 10000 node2001.delcatty.gent.vsc
    $ hostname
    node2001.delcatty.os

.. note:: Starting the SSH tunnel will only work if you have an HOD cluster running on the specified workernode.
          If not, you may see the connection 'hang' rather than fail. To cancel to connection attempt, use Ctrl-C.

.. note:: When first connecting to a workernode, you will see a request to accept the RSA key fingerprint for that
          workernode, as shown below. If you are confident you are connecting to the right workernode, enter '`yes`'::

            The authenticity of host 'node2001.delcatty.gent.vsc (<no hostip for proxy command>)' can't be established.
            RSA key fingerprint is 00:11:22:33:44:55:66:77:88:99:aa:bb:ee:dd:ee:ff.
            Are you sure you want to continue connecting (yes/no)? yes
            Warning: Permanently added 'node2001.delcatty.gent.vsc' (RSA) to the list of known hosts.

.. _start_SSH_tunnel_windows:

Starting the SSH tunnel using PuTTy in Windows
++++++++++++++++++++++++++++++++++++++++++++++

With your saved session configured, open the proxy session.


.. _browser_proxy_configuration:

Browser SOCKS proxy configuration
---------------------------------

To access the web user interface(s) of your running HOD cluster, you need to configure your browser
to use the SSH tunnel as a proxy.

Basically, you need to:

* define ``localhost`` (i.e., your own system) as a SOCKS proxy in your browser, using the port that you used
  when setting up the SSH tunnel (e.g., ``10000``)
* make sure that the proxy will also be used when entering ``https://localhost:<port>`` as a URL in your browser
* enter ``https://localhost:<port>`` as a URL in your browser, with ``<port>`` the port number for the web UI
  you want to connect to (see :ref:`web_ui_ports`)

The pages linked below provide a detailed walkthrough with screenshots on how to configure some commonly used
browsers:

* :ref:`Firefox (Windows, OS X, Linux) <browser_proxy_firefox>`
* :ref:`Chrome, Safari (OS X) <browser_proxy_chrome_safari_osx>`
* :ref:`Chrome (Windows) <browser_proxy_chrome_windows>`

.. note::
  Keep in mind that using the proxy will only work while you have access to the workernode for which the SSH tunnel
  was set up, i.e. while the HOD cluster is running, and while you are able to connect to the HPC infrastructure.

  To reset your browser configuration back to normal, simply disable the proxy in your browser configuration.

.. _web_ui_ports:

Ports for web user interfaces
-----------------------------

Once you have set up an SSH tunnel (see :ref:`ssh_tunnel`) and have configured your browsers to use it as
a SOCKS proxy (see :ref:`browser_proxy_configuration`), you can connect to the web user interfaces available in your
running HOD cluster via::

    http://localhost:<port>

The port number to use depends on the particular web user interface you want to connect to, see below.

.. note:: The command ``netstat -tulpn`` may be helpful in figuring out the ports being used by the running services.

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

.. _web_ui_ports_spark:

Ports for Spark web services
****************************

* ``4040``: information about running Spark application


.. note:: If multiple Spark applications (SparkContexts) are running, their web UI will be available via
          successive ports beginning with 4040 (4041, 4042, etc).

(see also https://spark.apache.org/docs/latest/monitoring.html)

.. _web_ui_ports_ipython:

Ports for IPython web services
******************************

* ``8888``: IPython notebook
