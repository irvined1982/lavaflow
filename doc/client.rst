Client Tools Installation
=========================

LavaFlow comes with client tooling for various scheduling environments which enable the administator to import data from
the cluster. This is typically done on the cluster front end, but it can be done on any machine that has access to the
log files regardless if that machine is actually part of the  cluster environment.

Download lavaFlow
-----------------

Use git to checkout `lavaFlow <https://github.com/irvined1982/lavaflowb>`_.::

    $ git clone https://github.com/irvined1982/lavaflow.git
    $ git submodule update --init --recursive

Install lavaFlow
----------------

Use setuptools to install the module.::

    $ sudo python setup.py install

This will install the lava-import-openlava script which is used to import data.

Openlava-python bindings
------------------------

In order to read and upload log files from openlava, you need to install the openlava python bindings.  These are used
only by the upload tools for openlava.  If you are not using openlava, you do not need to install these.

The openlava import client does not need to communicate with the cluster, it does however require access to the openlava
API, so openlava will need to be built even if it is not active.  This is in order to parse the log files.  Openlava
installation and configuration is out of hte scope of this document.  It is however assumed that the openlava
libraries are available.


Install the Openlava python bindings.::

    $ git clone https://github.com/irvined1982/openlava-python.git
    $ cd openlava-python/openlava/
    $ python setup.py install
