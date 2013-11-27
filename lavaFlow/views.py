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
from django.shortcuts import render,render_to_response
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
	data=json.loads(request.body)
	if data['event_type']==1: # Job New Event
		(cluster, created)=Cluster.objects.get_or_create(name=cluster_name)
		(user, created)=User.objects.get_or_create(name=data['user_name'])
		(submit_host, created)=Host.objects.get_or_create(name=data['submit_host'])
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
			js.submit_host=submit_host
			limit=OpenLavaResourceLimit()
			for k,v in data['resource_limits'].items():
				setattr(limit,k,v)
			limit.save()
			js.resource_limits=limit
			for item in ['user_id','num_processors','begin_time','termination_time','signal_value','checkpoint_period','restart_pid','host_specification','host_factor','umask','resource_request','cwd','checkpoint_dir','input_file','output_file','error_file','input_file_spool','command_spool','job_spool_dir','submit_home_dir','job_file','dependency_condition','job_name','command','num_transfer_files','pre_execution_cmd','email_user','nios_port','max_num_processors','schedule_host_type','login_shell','user_priority']:
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
		(submit_host, created)=Host.objects.get_or_create(name=data['submit_host'])
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
	
				for i in ['user_id','begin_time','termination_time','resource_request','cwd','input_file','output_file','error_file','input_file_spool','command_spool','job_file','host_factor','job_name','dependency_condition','pre_execution_cmd','email_user','exit_status','max_num_processors','login_shell','array_index','max_residual_mem','max_swap']:
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


def get_attempts(start_time_js, end_time_js, exclude_string, filter_string):
	start_time=int(int(start_time_js)/1000)
	end_time=int(int(end_time_js)/1000)
	filter_args=filter_string_to_params(filter_string)
	exclude_args=filter_string_to_params(exclude_string)
	attempts=Attempt.objects.all()
	if start_time:
		attempts=attempts.filter(end_time__gte=start_time)
	if end_time:
		attempts=attempts.filter(job__submit_time__lte=end_time)
	for key,val in filter_args.items():
		attempts=attempts.filter(**{key:val})
	for key,val in exclude_args.items():
		attempts=attempts.exclude(**{key:val})
	return attempts

@cache_page(60 * 60 * 2)
def utilization_table(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
	start_time_js=int(start_time_js)
	end_time_js=int(end_time_js)
	attempts=get_attempts(start_time_js, end_time_js, exclude_string, filter_string)
	group_args=group_string_to_group_args(group_string)
	if len(group_args)>0:
		attempts=attempts.values(*group_args)
	annotations=[]
	aggs=['pend_time','wall_time','cpu_time']
	for i in aggs:
		annotations.append(Avg(i))
		annotations.append(Min(i))
		annotations.append(Max(i))
		annotations.append(Sum(i))
	rows=[]
	header=[]
	nice_names={
			'num_processors':"Num Slots",
			'cluster__name':"Cluster",
			'status__name':"Exit Reason",
			}
	for a in group_args:
		field={}
		field['name']=a
		if a in nice_names:
			field['nice_name']=nice_names[a]
		else:
			field['nice_name']=a
		header.append(field)
	
	for r in attempts.annotate(*annotations):
		row={
				'groups':[]
			}
		for field in group_args:
			f={}
			f['name']=field
			if field in nice_names:
				f['nice_name']=nice_names[field]
			else:
				f['nice_name']=field

			f['value']=r[field]
			row['groups'].append(f)

		for a in aggs:
			for i in ["avg","min","max","sum"]:
				name="%s__%s" % (a,i)
				row[name]=datetime.timedelta(seconds=int(r[name]))
		rows.append(row)

	return render(request, "lavaFlow/widgets/utilization_chart.html", {'header':header,'rows':rows})


@cache_page(60 * 60 * 2)
def utilization_data(request, start_time_js=0, end_time_js=0, exclude_string="",  filter_string="", group_string=""):
	start_time_js=int(start_time_js)
	end_time_js=int(end_time_js)
	attempts=get_attempts(start_time_js, end_time_js, exclude_string, filter_string)

	# Only get the values we actually want - this is then
	# done in one request and is much faster
	values=[
			"job__submit_time",
			"start_time",
			"end_time",
			"num_processors",
			]
	group_args=group_string_to_group_args(group_string)
	values.extend(group_args)
	attempts=attempts.values(*values)

	serieses={}
	event_times=[]

	for attempt in attempts:
		# Build the series name from the grouping...
		series_name=""
		for n in group_args:
			series_name= u"%s%s" % (series_name,   attempt[n])

		# Get the name of the series for pending and running data
		if len(series_name)>0:
			pend_series_name="%s Pending" % series_name
		else:
			pend_series_name="Pending"

		if len(series_name)>0:
			run_series_name="%s Running" % series_name
		else:
			run_series_name="Running"

		# Check that both series exist.
		if not pend_series_name in serieses:
			serieses[pend_series_name]={start_time_js:0,end_time_js:0}
		pend_series=serieses[pend_series_name]

		if not run_series_name in serieses:
			serieses[run_series_name]={start_time_js:0,end_time_js:0}
		run_series=serieses[run_series_name]

		# Get the values
		submit_time = int(attempt['job__submit_time']) * 1000
		start_time = int(attempt['start_time']) * 1000
		end_time = int(attempt['end_time']) * 1000
		num_processors = attempt['num_processors']


		# Sanitize them so that they do not go out of bounds
		if submit_time < start_time_js:
			submit_time=start_time_js
		if start_time < start_time_js:
			start_time=start_time_js
		if end_time > end_time_js:
			end_time=end_time_js

		# All series shall have a time for each entry, this
		# makes the chart smoother as there is a data point
		# for each action in both pending and running jobs.
		for time in [submit_time, start_time, end_time]:
			for series in [run_series, pend_series]:
				if time not in series:
					series[time]=0
			if time not in event_times:
				event_times.append(time)

		# Adjust the value accordingly
		pend_series[submit_time] += num_processors
		pend_series[start_time] -= num_processors


		run_series[start_time] += num_processors
		run_series[end_time] -= num_processors

	series_int=[]

	# Process each series
	series_data={}
	for series_name, series in serieses.iteritems():
		# Change the series from the integral to the actual
		# total value.
		for time in sorted(series.keys()):
			# if it is a mid value, insert a value next to it
			# lsf has a 1 second resolution, so put it a milisecond before
			# this means graphs will look square, which is more accurate than peaks.
			if time-1 <= end_time_js and time-1 >= start_time_js:
				if time-1 not in series:
					series[time-1]=0
					if time-1 not in event_times:
						event_times.append(time-1)
			if time+1 <= end_time_js and time+1 >= start_time_js:
				if time+1 not in series:
					series[time+1]=0
					if time+1 not in event_times:
						event_times.append(time+1)

		values=[]
		total_slots_at_time=0
		times=[]
		for time in sorted(series.keys()):
			value=series[time]
			total_slots_at_time += value
			values.append(total_slots_at_time)
			times.append(time)
		ip=interpolate.interp1d(times, values, kind='nearest',bounds_error=False,fill_value=0.0)
		series_data[series_name]=ip

	# If there are more datapoints than can be processed
	# Then downsample...
	max_length=500
	if len(event_times) > max_length:
		interval=int((end_time_js-start_time_js)/max_length)
		event_times=range( start_time_js, end_time_js, interval)

	for series_name, ip in series_data.iteritems():
		d3_series={
				'key':series_name,
				'values':[]
				}
		# Now populate with interpolated data.
		for time in sorted(event_times):
			d3_series['values'].append({'x':time,'y':int(ip(time))})
		series_int.append(d3_series)

	return HttpResponse(json.dumps(series_int, indent=1), content_type="application/json")


@cache_page(60 * 60 * 2)
def utilization_view(request, start_time_js=None, end_time_js=None, exclude_string="none", filter_string="none", group_string=""):
	#
	if start_time_js == None:
		start_time_js=-1
	if end_time_js == None:
		end_time_js = -1

	data={
			'filters':json.dumps(filter_string_to_params(filter_string)),
			'excludes':json.dumps(filter_string_to_params(exclude_string)),
			'report_range_url':reverse('lf_get_report_range', kwargs={'filter_string':filter_string, 'exclude_string':exclude_string}),
			'build_filter_url':reverse('lf_build_filter'),
			'start_time':start_time_js,
			'end_time':end_time_js,
		}
	return render(request, "lavaFlow/utilization_view.html",data)

def util_total_attempts(request, start_time_js=None, end_time_js=None, exclude_string="", filter_string="", group_string=""):
	start_time_js=int(start_time_js)
	end_time_js=int(end_time_js)
	attempts=get_attempts(start_time_js, end_time_js, exclude_string, filter_string)
	count=attempts.count()
	data={
			'count':count,
		}
	return HttpResponse(json.dumps(data), content_type="application/json")


def util_report_range(request, exclude_string="", filter_string=""):
	ONE_DAY=24*60*60*60 # 1 day in seconds
	filter_args=filter_string_to_params(filter_string)
	exclude_args=filter_string_to_params(exclude_string)
	attempts=Attempt.objects.all()
	for key,val in filter_args.items():
		attempts=attempts.filter(**{key:val})
	for key,val in exclude_args.items():
		attempts=attempts.exclude(**{key:val})

	count=attempts.count()
	end_time=0
	start_time=0
	suggested_end_time=end_time
	suggested_start_time=end_time

	if count > 0:
		start_time=attempts.order_by('job__submit_time')[0].job.submit_time
		end_time=attempts.order_by('-end_time')[0].end_time
		suggested_end_time=end_time
		suggested_start_time=end_time-ONE_DAY
		if suggested_start_time<start_time:
			suggested_start_time=start_time

	data={
			'count':count,
			'end_time':end_time * 1000,
			'start_time':start_time * 1000,
			'suggested_end_time':suggested_end_time * 1000,
			'suggested_start_time':suggested_start_time * 1000,
	}

	return HttpResponse(json.dumps(data), content_type="application/json")

def group_string_to_group_args(group_string):
	if group_string=="none":
		return []
	group_args=[]
	if len(group_string)>0:
		group_args=group_string.split("/")
	return group_args

def filter_string_to_params(filter_string):
	# Build the additional filters
	if len(filter_string)<1 or filter_string=="none":
		return {}
	filter_args={}
	for f in filter_string.split("/"):
		(filter, dot, value)=f.partition(".")
		if filter.endswith("__in"): # multi value...
			if filter not  in filter_args:
				filter_args[filter]=[]
			filter_args[filter].append(value)
		else:
			filter_args[filter]=value
	return filter_args

# data.filters{name:[values]

@csrf_exempt
def build_filter(request):
	data=json.loads(request.body)

	view=data['view']
	start_time_js=data['start_time_js']
	if start_time_js<0:
		start_time_js=0
	end_time_js=data['end_time_js']
	if end_time_js<0:
		end_time_js=0

	values=[]
	for name,value in data['filters'].iteritems():
		if name.endswith('__in'): #list context
			values.extend([ "%s.%s" % (name,val) for val in value ])
		else:
			values.append("%s.%s" % (name, value))
	filter_string= "/".join(values)
	if len(filter_string)<1:
		filter_string="none"

	values=[]
	for name,value in data['excludes'].iteritems():
		if name.endswith('__in'): #list context
			values.extend([ "%s.%s" % (name,val) for val in value ])
		else:
			values.append("%s.%s" % (name, value))
	exclude_string= "/".join(values)
	if len(exclude_string)<1:
		exclude_string="none"

	group_string="/".join(data['groups'])
	if len(group_string)<1:
		group_string="none"

	if view=='get_report_range':
		url=reverse(view, kwargs={ 'exclude_string':str(exclude_string), 'filter_string':str(filter_string)})
	else:
		url=reverse(view, kwargs={'start_time_js':int(start_time_js), 'end_time_js':int(end_time_js), 'exclude_string':str(exclude_string), 'filter_string':str(filter_string), 'group_string':str(group_string)})
	url=request.build_absolute_uri(url)

	return HttpResponse(json.dumps({'url':url}), content_type="application/json")


