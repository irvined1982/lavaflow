
LavaFlow Server Installation
============================

LavaFlow is a django application. It is installed and configured just like any other Django application would be. The
following steps are required to install LavaFlow.

Install Django
--------------

If you have not already done so, `Install Django <https://docs.djangoproject.com/en/1.6/intro/install/>`_.

Django Project
--------------

Create and configure a django project. This can be done by following `these steps <https://docs.djangoproject.com/en/1.6/intro/tutorial01/#creating-a-project>`_.

Web Server Configuration
------------------------

Configure Lavaflow as a WSGI application as prescribed in the Django tutorial.

Download lavaFlow
-----------------

Use git to checkout `lavaFlow <https://github.com/irvined1982/lavaflowb>`_.::

    $ git clone https://github.com/irvined1982/lavaflow.git
    $ git submodule update --init --recursive

Install lavaFlow
----------------

Use setuptools to install the module.::

    $ sudo python setup.py install

Activate lavaFlow
-----------------

Install lavaFlow as an application in your django project.::

    INSTALLED_APPS = (
    ...
        'lavaFlow',
    ...
    )

Configure the URLs for lavaFlow. Open urls.py in your django project, and include the url configuration for lavaFlow::

    urlpatterns = patterns('',
        url(r'^', include('lavaFlow.urls')),

You can now view lavaFlow by visiting your web server.
