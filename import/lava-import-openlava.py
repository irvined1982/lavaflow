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
from openlava import EventLog, OpenLava
parser = argparse.ArgumentParser(description='Import OpenLava Log Files into LavaFlow')
parser.add_argument('log_file', metavar='LOGFILE', type=str, help="Path to Logfile")
parser.add_argument('url', metavar='URL', type=str, help="URL to LavaFlow server")
parser.add_argument('--cluster_name', metavar="NAME", type=str, help="Optional cluster name to use, default is to get lsf cluster name", default=None)
args = parser.parse_args()

# Open the event log file
el=EventLog(file_name=args.log_file)

# Get the cluster name
if args.cluster_name:
	cluster_name=args.cluster_name
else:
	cluster_name=OpenLava.get_cluster_name()

# Get the URL to submit to
url=args.url.rstrip("/")
url+="/clusters/%s/import/openlava" % cluster_name



def upload(rows):
		request = urllib2.Request(url, json.dumps(rows), {'Content-Type': 'application/json'})
		try:
			f = urllib2.urlopen(request)
			f.close()
		except:
			pass
		print "Imported %d rows." % row_num



# Iterate through the log file and upload in batches of 200
row_num=0
rows=[]
for row in el:
	row_num += 1
	rows.append(json.loads(OpenLava.dumps(row)))# memory is reused in structs...
	if row_num % 200 == 0:
		upload(rows)
		rows=[]

if len(rows)>0:
	upload(rows)
