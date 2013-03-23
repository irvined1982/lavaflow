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
#
# $Rev: 158 $:   
# $Author: irvined $: 
# $Date: 2012-10-31 23:42:17 +0100 (Wed, 31 Oct 2012) $:  
#

import sys
import traceback
import csv
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from lavaFlow.accounting import *
from lavaFlow.models import *

# Global cluster
c=None
# User object cache
users={}
# Host object cache
hosts={}
# Queue Object Cache
queues={}

class Command(BaseCommand):
	option_list=BaseCommand.option_list + (
		make_option("-f", "--file", dest="filename",help="Read from lsb accounting FILE", metavar="FILE"),
		make_option("-c", "--cluster", dest="cluster",help="Cluster name", metavar="CLUSTER"),
	)
	def handle(self, *args, **options):
		if not options['cluster']:
			print "No cluster specified."
			sys.exit(253)
		if not options['filename']:
			print "No filename specified."
			sys.exit(253)
		try:
			acctf=open(options['filename'],'rb')
		except IOError as e:
			print 'File cannot be opened.'
			sys.exit(254)
		rowNum=0
		skipped=0
		f=csv.reader(acctf, delimiter=' ', quotechar='"')
		(c, created)=Cluster.objects.get_or_create(name=options['cluster'])
		for row in f:
			try:
				if row[0]=="JOB_FINISH":
					job_finish(c,row)
					rowNum+=1
					if rowNum % 100==0:
						print "Row: %s" %rowNum
			except KeyboardInterrupt:
				raise
			except:
				traceback.print_exc()
				print row

def job_finish(c,row):
	job=JobFinishEvent(row)
	# Find or create the user
	try:
		user=users[job.user_name]
	except:
		(user,created)=User.objects.get_or_create(user_name=job.user_name)
		users[job.user_name]=user

	# find or create the submit host
	try:
		submit_host=hosts[job.submit_host]
	except:
		(submit_host,created)=Host.objects.get_or_create(hostName=job.submit_host)
		hosts[job.submit_host]=submit_host

	# find or create the job, don't cache it.
	jobData={
		'job_id':job.job_id,
		'user':user,
		'submit_host':submit_host,
		'submit_time':job.submit_time,
		'cluster':c,
	}
	(j, created)=Job.objects.get_or_create(job_id=job.job_id, cluster=c, user=user,submit_time=job.submit_time, defaults=jobData)

	# Find or create the element in the project
	elementData={
		'elementId':job.idx,
	}
	(e, created)=j.elements.get_or_create(elementId=job.idx, defaults=elementData)

	# find or create the queue
	try:
		q=queues[job.queue]
	except:
		(q, created)=Queue.objects.get_or_create(name=job.queue)
		queues[job.queue]=q

	# create the run if needed
	runData={
		'element':e,
		'num_processors':job.num_processors,
		'start_time':job.start_time,
		'end_time':job.end_time,
		'wall_time':job.wall_time,
		'cpu_time':job.wall_time*job.num_processors,
		'pend_time':job.pend_time,
		'queue':q,
	}

	(r,created)=Run.objects.get_or_create(element=e,start_time=job.start_time, defaults=runData)
	if created:
		# Add the projects to the run
		(p, created)=Project.objects.get_or_create(name=job.project_name, cluster=c)
		r.projects.add(p)
		for host in job.execHosts:
			cores=1
			if "*" in host:
				cores,star,host=host.partition("*")
			try:
				h=hosts[host]
			except:
				(h,created)=Host.objects.get_or_create(hostName=host)
				hosts[host]=h
			r.executions.create(host=h, run=r, num_processors=cores)
		rf=RunFinishInfo()
		rf.run=r
		rf.options=job.options
		rf.num_processors=job.num_processors
		rf.begin_time=job.begin_time
		rf.term_time=job.term_time
		rf.user_name=job.user_name
		rf.requested_resources=job.requested_resources
		rf.dependency_conditions=job.dependency_conditions
		rf.pre_execution_command=job.pre_execution_command
		rf.cwd=job.cwd
		rf.input_file=job.input_file
		rf.outFile=job.outFile
		rf.errFile=job.errFile
		rf.job_file=job.job_file
		(js, created)=JobStatus.objects.get_or_create(job_status=job.job_status)
		rf.job_status=js
		rf.host_factor=job.host_factor
		rf.job_name=job.job_name
		rf.command=job.command
		rf.utime=job.utime
		rf.stime=job.stime
		rf.maxrss=job.maxrss
		rf.ixrss=job.ixrss
		rf.ismrss=job.ismrss
		rf.idrss = job.idrss
		rf.isrss = job.isrss
		rf.minflt = job.minflt
		rf.majflt = job.majflt
		rf.nswap = job.nswap
		rf.inblock = job.inblock
		rf.oublock = job.oublock
		rf.ioch = job.ioch
		rf.msgsnd = job.msgsnd
		rf.msgrcv = job.msgrcv
		rf.nsignals = job.nsignals
		rf.nvcsw = job.nvcsw
		rf.nivcsw = job.nivcsw
		rf.exutime = job.exutime
		rf.email_user = job.email_user
		rf.project_name = job.project_name
		rf.exit_status_code = job.exit_status_code
		rf.max_num_processors= job.max_num_processors
		if len(job.login_shell)<RunFinishInfo._meta.get_field('login_shell').max_length:
			rf.login_shell = job.login_shell
		else:
			rf.login_shell="TRUNCATED"
		rf.timeEvent = job.timeEvent
		rf.idx = job.idx
		rf.max_residual_mem = job.max_residual_mem
		rf.max_swap = job.max_swap
		rf.input_file_spool = job.input_file_spool
		rf.command_spool = job.command_spool
		rf.rsvId = job.rsvId
		rf.sla = job.sla
		rf.exceptMask = job.exceptMask
		rf.additionalInfo = job.additionalInfo
		er=job.termInfo.name
		if er=="TERM_UNKNOWN":
			er="%s_%s" % (rf.job_status.job_status,rf.exit_status_code) 
		(ei,created)=ExitReason.objects.get_or_create(name=er, defaults={'description':job.termInfo.description,'value':job.termInfo.number})
		rf.exit_reason = ei
		rf.warningTimePeriod = job.warningTimePeriod
		rf.warningAction = job.warningAction
		rf.save()
		for host in job.requested_hosts:
			cores=1
			try:
				h=hosts[host]
			except:
				(h,created)=Host.objects.get_or_create(hostName=host)
				hosts[host]=h
			rf.requested_hosts.add(h)

