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
# Create your views here.
from scipy import interpolate
import base64
import re
import uuid
import datetime
import json
import time
import tempfile
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.db.models import Count
from django.db.models import Sum
from django.template import RequestContext
from django.http import Http404
from lavaFlow.models import *
log=logging.getLogger(__name__)
@csrf_exempt
def openlava_import(request,cluster_name):
	data=json.loads(request.raw_post_data)
	if data['event_type']==1: # Job New Event
		(cluster, created)=Cluster.objects.get_or_create(name=cluster_name)
		(user, created)=User.objects.get_or_create(name=data['user_name'])
		(submit_host, created)=Host.objects.get_or_create(name=data['submission_host'])
		(job, created)=Job.objects.get_or_create(cluster=cluster, job_id=data['job_id'], user=user, submit_host=submit_host, submit_time=data['submit_time'])
		(queue, created)=Queue.objects.get_or_create(name=data['queue'], cluster=cluster)

		try:
			job.jobsubmitopenlava
		except:
			js=JobSubmitOpenLava()
			js.job=job
			(project, created)=Project.objects.get_or_create(name=data['project_name'])
			js.project=project
			js.user=user
			#resource limits
			js.queue=queue
			js.submission_host=submit_host
			limit=OpenLavaResourceLimit()
			for k,v in data['resource_limits'].items():
				setattr(limit,k,v)
			limit.save()
			js.resource_limits=limit
			for item in ['user_id','num_processors','begin_time','termination_time','signal_value','checkpoint_period','restart_pid','host_specification','host_factor','umask','resource_request','cwd','checkpoint_directory','input_file','output_file','error_file','input_spool','command_spool','spool_directory','submission_home_dir','job_file','dependency_condition','job_name','command','num_transfer_files','pre_execution_command','email_user','nios_port','max_num_processors','schedule_host_type','login_shell','user_priority']:
				setattr(js,item,data[item])
			js.save()
			for option in data['options']:
				(o,created)=OpenLavaSubmitOption.objects.get_or_create(code=option['status'],name=option['name'],description=option['description'])
				js.options.add(o)
			for host in data['asked_hosts']:
				(h,created)=Host.objects.get_or_create(name=host)
				js.asked_hosts.add(h)
			for fl in data['transfer_files']:
				f=OpenLavaTransferFile()
				f.submission_file_name=fl['submission_file_name']
				f.execution_file_name=fl['execution_file_name']
				f.save()
				js.transfer_files.add(f)

	if data['event_type']==10:
		# Job Finish Event
		(cluster, created)=Cluster.objects.get_or_create(name=cluster_name)
		(user, created)=User.objects.get_or_create(name=data['user_name'])
		(submit_host, created)=Host.objects.get_or_create(name=data['submission_host'])
		(job, created)=Job.objects.get_or_create(cluster=cluster, job_id=data['job_id'], user=user, submit_host=submit_host, submit_time=data['submit_time'])
		(task, created)=Task.objects.get_or_create(cluster=cluster, job=job, user=user,task_id=data['array_index'])
		num_processors=data['num_processors']
		start_time=data['start_time']
		if start_time==0: # Job was killed before starting
			start_time=data['time']
		end_time=data['end_time']
		wall_time=end_time-start_time
		cpu_time=wall_time*num_processors
		pend_time=data['time']-data['submit_time']
		if start_time>0: # 0 == job didn't start
			pend_time=start_time-data['submit_time']

		(queue, created)=Queue.objects.get_or_create(name=data['queue'], cluster=cluster)
		(status, created)=JobStatus.objects.get_or_create(
				code=data['job_status']['status'],
				name=data['job_status']['name'],
				description=data['job_status']['description']
				)
		(attempt, created)=Attempt.objects.get_or_create(
				cluster=cluster,
				job=job,
				task=task,
				start_time=start_time,
				defaults={
					'user':user,
					'num_processors':num_processors,
					'end_time':end_time,
					'cpu_time':cpu_time,
					'wall_time':wall_time,
					'pend_time':pend_time,
					'queue':queue,
					'status':status,
					'command':data['command'],
				},
				)
		if created:
			for host in data['execution_hosts']:
				(execution_host, created)=Host.objects.get_or_create(name=host)
				attempt.execution_hosts.add(execution_host)
			(project, created)=Project.objects.get_or_create(name=data['project_name'])
			attempt.projects.add(project)
			try:
				attempt.openlavaexitinfo
			except:
				
				ol=OpenLavaExitInfo()
				ol.attempt=attempt
	
				(project, created)=Project.objects.get_or_create(name=data['project_name'])
				resource_usage=OpenLavaResourceUsage()
				for i,v in data['resource_usage'].items():
					setattr(resource_usage,i,v)
				resource_usage.save()
	
				for i in ['user_id','begin_time','termination_time','resource_request','cwd','input_file','output_file','error_file','input_spool','command_spool','job_file','host_factor','job_name','dependency_condition','pre_execution_command','email_user','exit_status','max_num_processors','login_shell','array_index','max_residual_mem','max_swap']:
					setattr(ol,i,data[i])
	
				ol.project=project
				ol.resource_usage=resource_usage
				ol.save()
				for option in data['options']:
					(o,created)=OpenLavaSubmitOption.objects.get_or_create(code=option['status'],name=option['name'],description=option['description'])
					ol.options.add(o)
				for host in data['asked_hosts']:
					(h,created)=Host.objects.get_or_create(name=host)
					ol.asked_hosts.add(h)
	return HttpResponse("OK", content_type="text/plain")


def utilization_data(request, starttime, endtime ):
	serieses={}
	attempts=Attempt.objects.filter(job__submit_time__lte=endtime, end_time__gte=starttime) # Only jobs that were submitted before the end time and ended after the start time
	print "Count: %s" % attempts.count()
	series_name=""

	starttime=int(starttime)*1000
	endtime=int(endtime)*1000

	for attempt in attempts:
		if len(series_name)>0:
			real_series_name="%s Pending" % series_name
		else:
			real_series_name="Pending"

		if not real_series_name in serieses:
			serieses[real_series_name]={starttime:0,endtime:0}
		series=serieses[real_series_name]

		submit_time=attempt.job.submit_time*1000
		if submit_time < starttime:
			submit_time=starttime

		start_time=attempt.start_time*1000
		if start_time < starttime:
			start_time=starttime

		end_time=attempt.end_time*1000
		if end_time > endtime:
			end_time=endtime

		num_processors=attempt.num_processors

		if submit_time not in series:
			series[submit_time]=0
		if start_time not in series:
			series[start_time]=0
		if end_time not in series:
			series[end_time]=0

		series[submit_time] += num_processors
		series[start_time] -= num_processors

		if len(series_name)>0:
			real_series_name="%s Running" % series_name
		else:
			real_series_name="Running"
		
		if not real_series_name in serieses:
			serieses[real_series_name]={}
			serieses[real_series_name]={starttime:0,endtime:0}
		series=serieses[real_series_name]

		if submit_time not in series:
			series[submit_time]=0
		if start_time not in series:
			series[start_time]=0
		if end_time not in series:
			series[end_time]=0

		series[start_time] += num_processors
		series[end_time] -= num_processors
		
	series_int=[]
	for sname,s in serieses.iteritems():
		total=0
		nv_ser={
				'key':sname,
				'values':[]
				}
		for time in sorted(s.keys()): # Make the series contain a running total
			if time < endtime and time>starttime:
				nv_ser['values'].append({'x':time-1,'y':total})

			total+=s[time]
			nv_ser['values'].append({'x':time,'y':total})
		series_int.append(nv_ser)
		print len(nv_ser['values'])
	return HttpResponse(json.dumps(series_int), content_type="application/json")







