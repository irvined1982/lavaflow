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
import logging
from gridengine_accounting import AccountEntry, AccountFile


def upload(rows):
    """
    Uploads a bunch of rows to the server.
    :param rows: Array of objects to try to upload
    :return: None
    """

    # loop X times, then bail on error
    request = urllib2.Request(url, json.dumps({'key': args.key, 'payload': rows}), {'Content-Type': 'application/json'})
    # Ensure server knows this is an AJAX request.
    request.add_header('HTTP_X_REQUESTED_WITH', 'XMLHttpRequest')
    request.add_header('X-Requested-With', 'XMLHttpRequest')
    # Set the CSRF token
    request.add_header('X-CSRFToken', token)
    failed = True
    count = 0
    # Try up to ten times to upload the data, after that bail out.
    while failed and (args.retry_forever or count < 10):
        count += 1
        try:
            f = urllib2.urlopen(request)
            data = json.load(f)
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
        sys.exit(1)


parser = argparse.ArgumentParser(description='Import OpenLava Log Files into LavaFlow')
parser.add_argument('cluster_name', metavar="CLUSTER", type=str, help="Name of cluster")
parser.add_argument('log_file', metavar='LOGFILE', type=str, help="Path to Logfile")
parser.add_argument('url', metavar='URL', type=str, help="URL to LavaFlow server")
parser.add_argument('key', metavar='KEY', type=str, help="Authentication key")
parser.add_argument('--chunk_size', metavar="CHUNK_SIZE", type=int, default=200,
                    help="Number of records to group together before sending to server")
parser.add_argument('--log_level', metavar="LOG_LEVEL", type=str, default="warn", help="Log level to use")
parser.add_argument("--retry_forever", action="store_true", default="False",
                    help="Keep trying, even when server responds with an error")

args = parser.parse_args()

numeric_level = getattr(logging, args.log_level.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.log_level)
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=numeric_level)


# Open the event log file
if not os.path.exists(args.log_file):
    logging.critical("Error: Path: %s does not exist. Exiting.\n" % args.log_file)
    sys.exit(1)
try:
    fh = open(args.log_file)
except IOError as e:
    logging.critical("Error: Unable to open %s: %s. Exiting.\n" % (args.log_file, str(e)))
    sys.exit(1)

cluster_name = args.cluster_name
logging.info("My cluster name is: %s" % cluster_name)


# Set the URLs to submit to
url = args.url.rstrip("/")
url += "/clusters/%s/import/gridengine" % cluster_name
logging.debug("My upload URL is: %s" % url)


# Set the url to get the CSRF token
token_url = args.url.rstrip("/")
token_url += "/get_token"
logging.debug("My token URL is: %s" % token_url)
token = None
try:
    token_request = urllib2.Request(token_url)
    f = urllib2.urlopen(token_request)
    data = json.load(f)
    if data['status'] != "OK":
        logging.critical("Error: Unable to get CSRF Token: %s. Exiting\n" % data['message'])
        sys.exit(1)
    token = data['data']['cookie']
    logging.debug("Got token: %s" % token)
except IOError as e:
    logging.critical("Error: Unable to get CSRF Token: %s. Exiting\n" % str(e))
    sys.exit(1)

acct_file = AccountFile(fh)
row_num = 0
rows = []
for row in acct_file:
    row_num += 1
    if len(rows) % args.chunk_size == 0:
        upload(rows)
        rows = []
    rows.append(row.to_json())
fh.close()

if len(rows) > 0:
    upload(rows)

logging.info("EOF Reached, exiting....")
sys.exit(0)


