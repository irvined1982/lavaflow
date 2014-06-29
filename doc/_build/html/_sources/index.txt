.. LavaFlow documentation master file, created by
   sphinx-quickstart on Sun Aug  3 11:38:20 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

LavaFlow creates useful reports on the usage of high performance compute clusters. LavaFlow takes data from the
batch scheduling system, monitoring, and other tooling, and creates reports that help administrators, managers,
and end users better understand their cluster environment. LavaFlow supports OpenLava and Grid Engine.

LavaFlow is written in Python, and uses the Django web framework. Reports are modular, new modules are easy to
create using templates and Djangos query set API. LavaFlow uses human readable RESTful URLS, making it easy to
automate, and share links to reports.


Contents:

.. toctree::
   :maxdepth: 3

   about
   features
   install
   import
   views
   models
   core_models

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

