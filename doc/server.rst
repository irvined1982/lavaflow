
LavaFlow Server Installation
============================

LavaFlow is a django application. It is installed and configured just like any other Django application would be. The
following steps are required to install LavaFlow.  Django has a bunch of documentation on
`installing Django <https://docs.djangoproject.com/en/1.6/intro/install/>`_, as well as documentation on how to
`configure <https://docs.djangoproject.com/en/1.6/intro/tutorial01/#creating-a-project>`_. a Django project.  Once
configured.  You will need to configure a database, mysql is recommended for larger clusters, for smaller datasets
SQLite3 will work just fine.  It is recommended to use WSGI to talk to the Django project, however FastCGI works just
fine too.  This documentation assumes Apache, however Lighttpd and any other supported by Django should also work just
fine.

.. CAUTION::

    If using WSGI, then Django must run within the very first Python sub interpreter created when
    Python is initialised, as the C extensions will cause the project to hang intermittently otherwise.
    Read `more details on the issue and its solution <https://code.google.com/p/modwsgi/wiki/ApplicationIssues#Python_Simplified_GIL_State_API>`_.

Prerequisites
-------------

Software Packages
^^^^^^^^^^^^^^^^^

LavaFlow requires Apache, (to serve the pages) Mysql, (To store the data) Django, (The application framework) Git, (To
download the code) and SciPy. (For number crunching.)

These can be installed as follows::

    $ sudo apt-get install apache2 libapache2-mod-wsgi mysql-server python-django python-mysqldb python-setuptools python-scipy git

Basic Apache Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^

First, create a directory inside the document root of the web server that will hold the static files.  These will
be served directly by the web server using an alias.::

    $ mkdir /var/www/django_static

Enable the SSL module, this isnt a hard requirement, but again a good practice - If you do not use mod SSL, then all log
data and passwords used to authenticate users to lavaFlow will be sent in the clear.::

    $ sudo a2enmod ssl
    ...
    Enabling module ssl.

Enable the SSL site.::

    $ sudo a2ensite default-ssl
    ....
    Enabling site default-ssl.

Enable the WSGI module::

    $ sudo a2enmod wsgi
    ...
    Enabling module wsgi

Enable mod-rewrite, this is used to automatically redirect users to the SSL enabled site.::

    $ a2enmod rewrite

Edit the configuration for the default site.::

    $ sudo vim /etc/apache2/sites-available/000-default.conf

Add the following text:::

    RewriteCond %{HTTPS} !=on
    RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]

It should look something like:::

    <VirtualHost *:80>
            ServerAdmin webmaster@localhost
            RewriteCond %{HTTPS} !=on
            RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]
            ErrorLog ${APACHE_LOG_DIR}/error.log
            CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>

Open the SSL configuration, add an alias for /static to the directory Django will use to store its static files.::

    $ sudo vim /etc/apache2/sites-available/default-ssl.conf

Add the following:::

    Alias /static /var/www/django_static

It should look something like:::

    <IfModule mod_ssl.c>
            <VirtualHost _default_:443>
                    Alias /static /var/www/django_static
                    ServerAdmin webmaster@localhost
                    ErrorLog ${APACHE_LOG_DIR}/error.log
                    CustomLog ${APACHE_LOG_DIR}/access.log combined
                    SSLEngine on
                    SSLCertificateFile      /etc/ssl/certs/ssl-cert-snakeoil.pem
                    SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key
                    <FilesMatch "\.(cgi|shtml|phtml|php)$">
                                    SSLOptions +StdEnvVars
                    </FilesMatch>
                    <Directory /usr/lib/cgi-bin>
                                    SSLOptions +StdEnvVars
                    </Directory>
                    BrowserMatch "MSIE [2-6]" \
                                    nokeepalive ssl-unclean-shutdown \
                                    downgrade-1.0 force-response-1.0
                    BrowserMatch "MSIE [17-9]" ssl-unclean-shutdown
            </VirtualHost>
    </IfModule>

Restart the web server, and check that it is working.  Visit the web server, you should be redirected to the SSL site.
The SSL site will have a self-signed certificate, which should cause your web browser to ask for permission before
opening.::

    $ sudo service apache2 restart

.. image:: images/static_files.*
    :width: 600px
    :align: center

Check that visiting /static opens the django_static directory.

Mysql Database
^^^^^^^^^^^^^^

Use the mysql client to create a new database that will be used by Django to store the data for LavaFlow.  Create a new
user and give them access to the database::

    $ mysql -u root -p
    mysql> create database django_lavaflow;
    mysql> GRANT ALL PRIVILEGES ON django_lavaflow.* to 'django_lavaflow'@'localhost' identified by 'lavaflow';

Django Project Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a new project using django-admin.::

    $ cd /var/www
    $ sudo django-admin startproject django_lavaflow

Edit the settings, and configure the database, and path to static files.::

    $ vim /var/www/django_lavaflow/django_lavaflow/settings.py

Configure the DATABASES option as follows:::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME':'django_lavaflow',
            'USER': 'django_lavaflow',
            'PASSWORD': 'lavaflow',

        }
    }

Set the path on the webserver to the static files.::

    STATIC_URL = '/static/'

Add a setting for the path on the filesystem where the static files are stored.::

    STATIC_ROOT = "/var/www/html/django_static/"

Sync the database, and collect the static files::

    $ cd /var/www/django_lavaflow
    $ python manage.py syncdb
    $ python manage.py collectstatic --noinput

Add the WSGI configuration to Apache.::

    $ sudo vim /etc/apache2/sites-available/default-ssl.conf

Add global configuration options for Pythons path, and the application group.  These need to be in the global section
and not inside the VirtualHost directive.::

    WSGIPythonPath /var/www/django_lavaflow
    WSGIApplicationGroup %{GLOBAL}

Inside the VirtualHost directive configure the daemon and script alias for the Django project.::

    WSGIDaemonProcess lavaflow python-path=/var/www/django_lavaflow processes=10 threads=15 display-name=%{GROUP}
    WSGIScriptAlias / /var/www/django_lavaflow/django_lavaflow/wsgi.py

The file should look something like:::

    WSGIPythonPath /var/www/django_lavaflow
    WSGIApplicationGroup %{GLOBAL}
    <IfModule mod_ssl.c>
            <VirtualHost _default_:443>
                    Alias /static /var/www/django_static
                    WSGIDaemonProcess lavaflow python-path=/var/www/django_lavaflow processes=10 threads=15 display-name=%{GROUP}
                    WSGIScriptAlias / /var/www/django_lavaflow/django_lavaflow/wsgi.py
                    ServerAdmin webmaster@localhost
                    ErrorLog ${APACHE_LOG_DIR}/error.log
                    CustomLog ${APACHE_LOG_DIR}/access.log combined
                    SSLEngine on
                    SSLCertificateFile      /etc/ssl/certs/ssl-cert-snakeoil.pem
                    SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key
                    <FilesMatch "\.(cgi|shtml|phtml|php)$">
                                    SSLOptions +StdEnvVars
                    </FilesMatch>
                    <Directory /usr/lib/cgi-bin>
                                    SSLOptions +StdEnvVars
                    </Directory>
                    BrowserMatch "MSIE [2-6]" \
                                    nokeepalive ssl-unclean-shutdown \
                                    downgrade-1.0 force-response-1.0
                    BrowserMatch "MSIE [17-9]" ssl-unclean-shutdown
            </VirtualHost>
    </IfModule>

Restart apache, and check that you can now view the Django project.::

    $ service apache2 restart

.. image:: images/django_basic_install.*
    :width: 600px
    :align: center

Visit the web server using your browser, at the root of the server, the Django 'Hello World' screen indicating that it is running
successfully should be visible.

.. image:: images/admin_login.*
    :width: 600px
    :align: center

Visiting /admin should show the Django admin interface log on screen.

.. image:: images/django_admin_home_nolava.*
    :width: 600px
    :align: center

After logging in, you should see the Django admin interface, with users and groups menu.

Installing LavaFlow
-------------------

Using git, checkout the latest version of LavaFlow from GitHub.::

    $ cd
    $ git clone --recursive https://github.com/irvined1982/lavaflow.git
    Cloning into 'lavaflow'...
    ...
    Submodule 'lavaFlow/static/lavaFlow/blockUI' (https://github.com/malsup/blockui.git) registered for path 'lavaFlow/static/lavaFlow/blockUI'
    Submodule 'lavaFlow/static/lavaFlow/nvd3' (https://github.com/novus/nvd3.git) registered for path 'lavaFlow/static/lavaFlow/nvd3'
    Submodule 'lavaFlow/static/lavaFlow/timepicker' (https://github.com/trentrichardson/jQuery-Timepicker-Addon.git) registered for path 'lavaFlow/static/lavaFlow/timepicker'
    Submodule 'lavaFlow/static/lavaFlow/visjs' (https://github.com/irvined1982/vis.git) registered for path 'lavaFlow/static/lavaFlow/visjs'
    ...
    $

Once checked out, install LavaFlow using setup.py.::

    $ cd lavaflow
    $ sudo python manage.py install

Once installed, add LavaFlow to the installed applications in the projects settings.::

    $ cd /var/www/django_lavaflow/
    $ sudo vim django_lavaflow/settings.py

Set INSTALLED_APPS to include LavaFlow, it should look something like:::

    INSTALLED_APPS = (
        'lavaFlow',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    )

Run syncdb to create the tables needed for LavaFlow, then collect the static files.::

    $ sudo python manage.py syncdb
    $ sudo python manage.py collectstatic --noinput

Update urls.py to include the url config for LavaFlow.::

    $ sudo vim django_lavaflow/urls.py

Add the following line to urlpatterns below the admin urls:::

    url(r'^', include('lavaFlow.urls')),

It should look something like this:::

    urlpatterns = patterns('',
        # Examples:
        # url(r'^$', 'django_lavaflow.views.home', name='home'),
        # url(r'^blog/', include('blog.urls')),

        url(r'^admin/', include(admin.site.urls)),
        url(r'^', include('lavaFlow.urls')),
    )

Restart Apache, and test that you can now view the LavaFlow page.::

    $ service apache2 restart

.. image:: images/empty_lava.*
    :width: 600px
    :align: center

As you have not imported any data yet, you should see an empty page with a warning message, this is normal, and shows
that LavaFlow is working and is ready to accept data from your clusters.

