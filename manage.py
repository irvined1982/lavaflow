#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    ## settings is the default - or write your own local_settings.py
    ## os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lavaFlow.local_settings")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lavaFlow.settings")
    ## default database settings - seriously recommended to override
    os.environ.setdefault("LAVAFLOW_DBNAME", "lavaflow")
    os.environ.setdefault("LAVAFLOW_DBHOST", "localhost")
    os.environ.setdefault("LAVAFLOW_DBUSER", "lavaflow")
    os.environ.setdefault("LAVAFLOW_DBPASS", "lavaflow")
    
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
