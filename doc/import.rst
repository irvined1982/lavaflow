Import Tools
============

The following commands can be used to import the log files and accounting information from each scheduler.  Use the admin interface to create keys that can be used to upload data to lavaFlow.


lava-import-openlava.py
-----------------------

.. program:: lava-import-openlava.py

Reads openlava log files and uploads them.  Will read and attempt to upload all entries in the file.  This is not desirable if you have large logfiles and want to upload regularly, for that you should use logtail or some other utility to only read entries that have not yet been uploaded.  There is no harm in re-uploading, but it is time expensive.

.. option:: log_file

The path to the log file to read, should be one of lsb.acct or lsb.events*

.. option:: url

Fully qualified URL to the lavaflow server.

.. option:: key

Pre shared key that will be used to verify the client has permission to publish to the server.

.. option:: cluster_name

Optional name of the cluster, if no cluster name is specified, will attempt to infer cluster name from openlava directly.

