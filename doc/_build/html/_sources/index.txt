LavaFlow
========

LavaFlow creates useful reports on the usage of high performance compute clusters. LavaFlow takes data from the
batch scheduling system, monitoring, and other tooling, and creates reports that help administrators, managers,
and end users better understand their cluster environment. LavaFlow supports OpenLava and Grid Engine.

LavaFlow is written in Python, and uses the Django web framework. Reports are modular, new modules are easy to
create using templates and Django's query set API. LavaFlow uses human readable RESTful URLS, making it easy to
automate, and share links to reports.

You can view a demo of LavaFlow

Contents
========
.. toctree::
   :maxdepth: 3

   about
   features
   server
   client
   import
   views
   core_models
   glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

