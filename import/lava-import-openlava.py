#!/usr/bin/env python
# Copyright 2014 David Irvine
#
# This file is part of LavaFlow
#
# LavaFlow is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# LavaFlow is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LavaFlow.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys
import urllib2
import json
import argparse
import time
from openlava import lsblib, lslib
import logging

parser = argparse.ArgumentParser(description='Import OpenLava Log Files into LavaFlow')
parser.add_argument('log_file', metavar='LOGFILE', type=str, help="Path to Logfile")
parser.add_argument('url', metavar='URL', type=str, help="URL to LavaFlow server")
parser.add_argument('key', metavar='KEY', type=str, help="Authentication key")
parser.add_argument("--tail_log", type=bool, action="store_true", default=False,
                    help="When enabled, will not exit when the end of the input file is reached.  \
                    Instead, it will wait for new data, or if the file is rotated, reopen the file \
                    and continue reading.")
parser.add_argument('--cluster_name', metavar="NAME", type=str,
                    help="Optional cluster name to use, default is to get lsf cluster name", default=None)
args = parser.parse_args()

# Open the event log file
if not os.path.exists(args.log_file):
    logging.critical("Error: Path: %s does not exist. Exiting.\n" % args.log_file)
    sys.exit(1)
try:
    fh = open(args.log_file)
except IOError as e:
    logging.critical("Error: Unable to open %s: %s. Exiting.\n" % (args.log_file, str(e)))
    sys.exit(1)

# Get the cluster name
if args.cluster_name:
    cluster_name = args.cluster_name
else:
    cluster_name = lslib.ls_getclustername()
if len(cluster_name) < 1:
    logging.critical("Error: Unable to determine clustername. Exiting.\n")
    sys.exit(2)

# Set the URLs to submit to
url = args.url.rstrip("/")
url += "/clusters/%s/import/openlava" % cluster_name

# Set the url to get the CSRF token
token_url = args.url.rstrip("/")
token_url += "/get_token"
token = None
try:
    token_request = urllib2.Request(token_url)
    f = urllib2.urlopen(token_request)
    data = json.load(f)
    if data['status'] != "OK":
        logging.critical("Error: Unable to get CSRF Token: %s. Exiting\n" % data['message'])
        sys.exit(1)
    token=data['data']['cookie']
except IOError as e:
    logging.critical("Error: Unable to get CSRF Token: %s. Exiting\n" % str(e))
    sys.exit(1)


def upload(rows):
    """
    Uploads a bunch of rows to the server.
    :param rows: Array of objects to try to upload
    :return: None
    """

    # loop X times, then bail on error
    request = urllib2.Request(url, json.dumps({'key':args.key, 'payload':rows}), {'Content-Type': 'application/json'})
    # Ensure server knows this is an AJAX request.
    request.add_header('HTTP_X_REQUESTED_WITH', 'XMLHttpRequest')
    request.add_header('X-Requested-With', 'XMLHttpRequest')
    # Set the CSRF token
    request.add_header('X-CSRFToken', token)
    failed = True
    count = 0
    # Try up to ten times to upload the data, after that bail out.
    while failed and count < 10:
        count += 1
        try:
            f = urllib2.urlopen(request)
            data=json.load(f)
            if data['status'] == "OK":
                logging.info("Imported %d rows." % row_num)
                failed = False
            else:
                logging.error("Error: Unable to import rows: %s\n" % data['message'])
            f.close()
        except IOError as e:
            logging.error("Error: Failed to import rows: %s\n" % str(e))
    if failed:
        logging.critical("Error: Retry timeout reached. Exiting.")


class OLDumper(json.JSONEncoder):
    """
    Encoder to dump OpenLava objects to JSON.
    """
    def default(self, obj):
        """
        Attempts to call __to_dict(), the method used to return a dictionary copy, on the supplied object.
        If not supported calls the parent classes default encoder, which will raise an exception if the data type
        is not a standard python object.
        :param obj: Object to encode
        :return: json serializable object
        """
        try:
            return getattr(obj, "__to_dict")()
        except AttributeError:
            return json.JSONEncoder.default(self, obj)


# Iterate through the log file and upload in batches of 200
row_num = 0
rows = []
while True:
    rec = lsblib.lsb_geteventrec(fh, row_num)
    if rec is None:
        if lsblib.get_lsberrno() == lsblib.LSBE_EOF:
            logging.info("EOF Reached, waiting on new data")
            time.sleep(20)
            continue
    if lsblib.get_lsberrno() == lsblib.LSBE_EVENT_FORMAT:
        logging.error("Bad Row: %s in %s" % (row_num, args.log_file))
        continue

    rows.append(json.loads(json.dumps(rec, cls=OLDumper)))
    # ^^converts to dictionary which does a full copy of the data

    row_num += 1
    if row_num % 200 == 0:
        upload(rows)
        rows = []

if len(rows) > 0:
    upload(rows)
fh.close()
