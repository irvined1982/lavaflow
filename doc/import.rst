Import Tools
============

For each type of cluster that LavaFlow supports, there is also a corresponding set of tooling to import data form that
cluster.  The usage of which is documented below.

Import Key
----------

.. image:: images/create_import_key.*
    :width: 600px
    :align: center

Regardless of how you are importing data, you will require a shared key, this is stored in the ImportKey table, and
is part of the admin interface.  Log into the django admin interface, and click on the ImportKey item under the
lavaFlow section.

Create a new ImportKey, setting the client_key to the value of the shared key, it is recommended that you use a
different key for each cluster, however there is no hard requirement to do so.

Openlava
--------

data from lsb.acct and lsb.events needs to be imported into LavaFlow, this is done using lava-import-openlava, a python
script that reads the log file using the python bindings for openlava, and uploads them using another API call to the
openlava web server.

Initial Import
^^^^^^^^^^^^^^

At first, it is likely you will have various log files, some of which have been rotated by the scheduler, others that
perhaps are from an older cluster that has been retired and you wish to import historical data.  In that case it is
generally easiest to just run lava-import-python on each file once before setting up any recurring import.

For each cluster you will typically have at least one lsb.acct file, and many lsb.events files, these are rotated to
lsb.events.n where n is a number indicating the index of the file, the bigger the number, the older the data in the
file.

If you are on an active openlava cluster, the following example will import all existing data::

    $ for i in $LSF_ENVDIR/../work/logdir/lsb.events* $LSF_ENVDIR/../work/logdir/lsb.acct*  ;
      do
       lava-import-openlava --chunk_size 500 --log_level=info $i http://MyLavaServer/lavaflow topSecretKey
      done

In this case, the chunk_size is set slightly higher than normal which will give a faster import, however if you make
this too high, it is possible that the server will timeout when importing, which will result in a fatal error.

If you are importing data from a machine that is not part of the openlava cluster, or you want to specify a specific
name for the cluster other than what is reported by the scheduling system, you should use the --cluster_name option.

Normal Import
^^^^^^^^^^^^^

Once you have historical data imported, you need to run the import script with the --tail_log option, this will read
the log file to completion, and wait on new data.  If the log file is rotated, it will automatically load the new file
each time.

These should, ideally be started at system boot.

If you have a cluster that has a very low rate of job turnover, it is advisable to reduce the chunk_size so that
data is uploaded more often.::

    lava-import-openlava --chunk_size 50 --tail_log --log_level=warn $LSF_ENVDIR/../work/logdir/lsb.events http://MyLavaServer/lavaflow topSecretKey
    lava-import-openlava --chunk_size 50 --tail_log --log_level=warn $LSF_ENVDIR/../work/logdir/lsb.events http://MyLavaServer/lavaflow topSecretKey

If you have issues with network reliability, you may wish to use the --retry_forever which will never give up in the
event that the server does not respond.

lava-import-openlava
^^^^^^^^^^^^^^^^^^^^
.. program:: lava-import-openlava

Reads openlava log files and uploads them.  Will read and attempt to upload all entries in the file.
This is not desirable if you have large logfiles and want to upload regularly, for that you should use
logtail or some other utility to only read entries that have not yet been uploaded.  There is no harm in
re-uploading, but it is time expensive.

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

.. option:: retry_forever

When enabled, will not exit when the end of the input file is reached.  Instead, it will wait for new data,
or if the file is rotated, reopen the file and continue reading.

.. option:: skip

Skip N number of lines from the start of the file.

lava-import-univa82
^^^^^^^^^^^^^^^^^^^

.. program:: lava-import-univa82.py

Reads Univa Grid Engine 8.2 log files and uploads them.  Will read and attempt to upload all entries in the file.
This is not desirable if you have large logfiles and want to upload regularly, for that you should use
logtail or some other utility to only read entries that have not yet been uploaded.  There is no harm in
re-uploading, but it is time expensive.

.. option:: log_file

    The path to the log file to read, should be one of lsb.acct or lsb.events*

.. option:: url

    Fully qualified URL to the lavaflow server.

.. option:: key

    Pre shared key that will be used to verify the client has permission to publish to the server.

.. option:: cluster_name

    Name of the cluster, if no cluster name is specified, will attempt to infer cluster name from openlava
    directly.

.. option:: chunk_size

    Number of records to group together before sending to server.

.. option:: log_level

    Log level to use, can be one of debug, info, warn, error, critical.

.. option:: retry_forever

    When enabled, will not exit when the end of the input file is reached.  Instead, it will wait for new data,
    or if the file is rotated, reopen the file and continue reading.


