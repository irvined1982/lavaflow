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
import argparse
from openlava import EventLog, OpenLava
parser = argparse.ArgumentParser(description='Import OpenLava Log Files into LavaFlow')
parser.add_argument('log_file', metavar='LOGFILE', type=str, help="Path to Logfile")
parser.add_argument('url', metavar='URL', type=str, help="URL to LavaFlow server")
args = parser.parse_args()
el=EventLog(file_name=args.log_file)
cluster_name=OpenLava.get_cluster_name()
url=args.url.rstrip("/")
url+="/clusters/%s/import/openlava" % cluster_name
for row in el:
	data=OpenLava.dumps(row)
	request = urllib2.Request(url, data, {'Content-Type': 'application/json'})
	f = urllib2.urlopen(request)
	f.close()
