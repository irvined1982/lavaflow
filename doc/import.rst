Openlava Import
***************

lavaFlow comes with a script that will read OpenLava log files, and upload data to the lavaFlow server, this tool can
continuously in the background, or via a cron job, or manually as required.

Installataion
=============

Openlava-python bindings
------------------------

In order to read and upload log files, you need to install the openlava python bindings.  These are used only by the
upload tools, generally you only need to install this on the master node of each cluster, this may or may not be the
machine you are running lavaFlow on.

Install the Openlava python bindings.::

    $ git clone https://github.com/irvined1982/openlava-python.git
    $ cd openlava-python/openlava/
    $ python setup.py install

Download lavaFlow
-----------------

Use git to checkout `lavaFlow <https://github.com/irvined1982/lavaFlow>`_.::

    $ git clone https://github.com/irvined1982/lavaflow.git
    $ git submodule update --init --recursive

Inside the import directory you will find the import scripts.

lava-import-openlava.py
=======================

.. program:: lava-import-openlava.py

Reads openlava log files and uploads them.  Will read and attempt to upload all entries in the file.
This is not desirable if you have large logfiles and want to upload regularly, for that you should use
logtail or some other utility to only read entries that have not yet been uploaded.  There is no harm in
re-uploading, but it is time expensive.::

    usage: lava-import-openlava.py [-h] [--tail_log] [--cluster_name NAME]
                                   [--chunk_size CHUNK_SIZE]
                                   [--log_level LOG_LEVEL] [--retry_forever]
                                   LOGFILE URL KEY

.. option:: log_file

The path to the log file to read, should be one of lsb.acct or lsb.events*

.. option:: url

Fully qualified URL to the lavaflow server.

.. option:: key

Pre shared key that will be used to verify the client has permission to publish to the server.

.. option:: tail_log

When enabled, will not exit when the end of the input file is reached.  Instead, it will wait for new data,
or if the file is rotated, reopen the file and continue reading.

.. option:: cluster_name

Optional name of the cluster, if no cluster name is specified, will attempt to infer cluster name from openlava
directly.

.. option:: chunk_size

Number of records to group together before sending to server.

.. option:: log_level

Log level to use, can be one of debug, info, warn, error, critical.

.. option::retry_forever

When enabled, will not exit when the end of the input file is reached.  Instead, it will wait for new data,
or if the file is rotated, reopen the file and continue reading.
