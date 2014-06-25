#!/usr/bin/env python
# Copyright 2011 David Irvine
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
import urllib2
import json
import argparse
from openlava import lsblib,lslib

parser = argparse.ArgumentParser(description='Import OpenLava Log Files into LavaFlow')
parser.add_argument('log_file', metavar='LOGFILE', type=str, help="Path to Logfile")
parser.add_argument('url', metavar='URL', type=str, help="URL to LavaFlow server")
parser.add_argument('key', metavar='KEY', type=str, help="Authentication key")
parser.add_argument('--cluster_name', metavar="NAME", type=str,
                    help="Optional cluster name to use, default is to get lsf cluster name", default=None)
args = parser.parse_args()

# Open the event log file
fh = open(args.log_file)

# Get the cluster name
if args.cluster_name:
    cluster_name = args.cluster_name
else:
    cluster_name = lslib.ls_getclustername()

# Get the URL to submit to
url = args.url.rstrip("/")
url += "/clusters/%s/import/openlava" % cluster_name


def upload(rows):
    request = urllib2.Request(url, json.dumps(rows), {'Content-Type': 'application/json'})
    try:
        f = urllib2.urlopen(request)
        f.close()
    except:
        pass
    print "Imported %d rows." % row_num

class OOLDumper(json.JSONEncoder):
    def default(self, obj):
        try:
            return getattr(obj, "__to_dict")()
        except ValueError:
            return json.JSONEncoder.default(self, obj)


# Iterate through the log file and upload in batches of 200
row_num = 0
rows = []
while(True):
    rec = lsblib.lsb_geteventrec(fh, row_num)
    if rec == None:
        if lsblib.get_lsberrno() == lsblib.LSBE_EOF:
            break
    if lsblib.get_lsberrno() == lsblib.LSBE_EVENT_FORMAT:
        print "Bad Row: %s in %s" % (row_num, args.log_file)
        continue

    rows.append(json.loads(json.dumps(rec, cls=OOLDumper)))
    # ^^converts to dictionary which does a full copy of the data

    row_num += 1
    if row_num % 200 == 0:
        upload(rows)
        rows = []

if len(rows) > 0:
    upload(rows)
