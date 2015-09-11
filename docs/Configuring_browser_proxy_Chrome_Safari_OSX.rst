.. _browser_proxy_chrome_safari_osx:

Browser proxy configuration for Chrome/Safari on OS X
=====================================================

.. note::
  Keep in mind that using the proxy will only work while you have access to the workernode for which the SSH tunnel
  was set up, i.e. while the HOD cluster is running, and while you are able to connect to the HPC infrastructure.

  To reset your browser configuration back to normal, simply disable the proxy in your browser configuration.

1. Navigate to the ``Proxies`` tab in the ``Advanded`` part of the ``Network`` section in ``System Preferences``

  * directly, via ``System Preferences``, ``Network``, ``Advanced``, ``Proxies`` tab
  * via Safari: ``Preferences``, ``Advanced``, ``Proxies: Change settings...``
  * via Chrome: ``Settings`` (or ``Preferences...``), ``Change proxy settings`` (enter ``proxy`` in ``Search settings``)

.. image:: img/browser_proxy_cfg/chrome_safari_osx /01_osx_network_proxies.png
    :scale: 50 %

2. Select ``SOCKS proxy``, enter ``localhost`` and port number that was used to set up the SSH tunnel (e.g., ``10000``)

   Clear the ``Bypass proxy settings for these Hosts & Domains`` box.

   Click ``OK`` to save the configuration.

.. image:: img/browser_proxy_cfg/chrome_safari_osx /02_socks_proxy.png
    :scale: 50 %

