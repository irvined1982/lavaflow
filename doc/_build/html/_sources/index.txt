LavaFlow
========

LavaFlow creates useful reports on the usage of high performance compute clusters. LavaFlow takes data from the
batch scheduling system, monitoring, and other tooling, and creates reports that help administrators, managers,
and end users better understand their cluster environment. LavaFlow supports OpenLava and Grid Engine.

LavaFlow is written in Python, and uses the Django web framework. Reports are modular, new modules are easy to
create using templates and Django's query set API. LavaFlow uses human readable RESTful URLS, making it easy to
automate, and share links to reports.

LavaFlow is `hosted on GitHub <https://github.com/irvined1982/lavaflow>`_, and you can try out
the `online demo <https://www.clusterfsck.io/dev/lavaFlow>`_.

Amazon AMI
----------
The following AMI is available in us-east-1: ami-9c38ebf4 - This is a ubuntu based image that has LavaFlow pre-installed
and ready to accept new data.  The default admin password is lavaflow.


Contents
========
.. toctree::
   :maxdepth: 3

   about
   features
   server
   client
   import
   developer
   glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

