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
from gridengine_accounting import AccountEntry, AccountFile
parser = argparse.ArgumentParser(description='Import Grid Engine Accounting Files into LavaFlow')
parser.add_argument('cluster', metavar="CLUSTER", type=str, help="Name of cluster")
parser.add_argument('log_file', metavar='LOGFILE', type=str, help="Path to Logfile")
parser.add_argument('url', metavar='URL', type=str, help="URL to LavaFlow server")
args = parser.parse_args()
log_file=open(args.log_file)
acct_file=AccountFile(log_file)

cluster_name=args.cluster
url=args.url.rstrip("/")
url+="/clusters/%s/import/gridengine" % cluster_name
row_num=0
for row in acct_file:
	if row_num % 100 == 0:
		print "Imported %d rows." % row_num
	row_num += 1
	data=row.to_json()
	request = urllib2.Request(url, data, {'Content-Type': 'application/json'})
	f = urllib2.urlopen(request)
	f.close()
