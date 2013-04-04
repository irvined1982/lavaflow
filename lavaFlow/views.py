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
import base64
import re
import uuid
import datetime
import json
import time
import MySQLdb
import tempfile
import logging
from django.views.decorators.csrf import csrf_exempt
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

@cache_page(60 * 15)
def clusterList(request):
	paginator = Paginator(Cluster.objects.all(), 30)
	page = request.GET.get('page')
	if not page:
		page=1
	try:
		clusters=paginator.page(page)
	except PageNotAnInteger:
		clusters=paginator.page(1)
	except EmptyPage:
		clusters=paginator.page(paginator.num_pages)
	return render_to_response("lavaFlow/clusterList.html",{'clusters':clusters},context_instance=RequestContext(request))

@cache_page(60 * 15)
def projectList(request):
	paginator = Paginator(Project.objects.all(), 30)
	page = request.GET.get('page')
	if not page:
		page=1
	try:
		projects=paginator.page(page)
	except PageNotAnInteger:
		projects=paginator.page(1)
	except EmptyPage:
		projects=paginator.page(paginator.num_pages)
	return render_to_response("lavaFlow/projectList.html",{'projects':projects},context_instance=RequestContext(request))

@cache_page(60 * 15)
def queueList(request):
	paginator = Paginator(Queue.objects.all(), 30)
	page = request.GET.get('page')
	if not page:
		page=1
	try:
		queues=paginator.page(page)
	except PageNotAnInteger:
		queues=paginator.page(1)
	except EmptyPage:
		queues=paginator.page(paginator.num_pages)
	return render_to_response("lavaFlow/queueList.html",{'queues':queues},context_instance=RequestContext(request))


@cache_page(60 * 15)
def hostList(request):
	paginator = Paginator(Host.objects.all(), 30)
	page = request.GET.get('page')
	if not page:
		page=1
	try:
		hosts=paginator.page(page)
	except PageNotAnInteger:
		hosts=paginator.page(1)
	except EmptyPage:
		hosts=paginator.page(paginator.num_pages)
	return render_to_response("lavaFlow/hostList.html",{'hosts':hosts},context_instance=RequestContext(request))


@cache_page(60 * 15)
def userList(request):
	paginator = Paginator(User.objects.all(), 30)
	page = request.GET.get('page')
	if not page:
		page=1
	try:
		users=paginator.page(page)
	except PageNotAnInteger:
		users=paginator.page(1)
	except EmptyPage:
		users=paginator.page(paginator.num_pages)
	return render_to_response("lavaFlow/userList.html",{'users':users},context_instance=RequestContext(request))


@cache_page(60 * 15)
def jobDetailView(request,id):
	job=get_object_or_404(Job,pk=id)
	return render_to_response('lavaFlow/jobDetailView.html',{'job':job,},context_instance=RequestContext(request))


@cache_page(60 * 15)
def runDetailView(request,id):
	run=get_object_or_404(Run,pk=id)
	return render_to_response('lavaFlow/runDetailView.html',{'run':run},context_instance=RequestContext(request))


@cache_page(60 * 15)
def jobSearchView(request):
	query = request.GET.get('jobid')
	jobs=None
	if query:
		try:
			query=int(query)
			jobs=Job.objects.filter(job_id=query)
		except ValueError:
			pass
	return render_to_response("lavaFlow/jobSearch.html",{'jobs':jobs},context_instance=RequestContext(request))


@csrf_exempt
def uploadData(request,cluster):
	if not request.method=="PUT":
		raise Http404("Only PUT requests supported")
	try:
		ob=json.loads(request.raw_post_data)
	except:
		raise
	for o in ob:
		process_element(cluster,o)
	return HttpResponse("OK",content_type="text/plain")

def process_element(cluster,ob):
	(cluster, created)=Cluster.objects.get_or_create(name=cluster)
	(user,created)=User.objects.get_or_create(user_name=ob['user_name'])
	(submit_host,created)=Host.objects.get_or_create(host_name=ob['submit_host'])
	jobData={
			'job_id':ob['job_id'],
			'user':user,
			'submit_host':submit_host,
			'submit_time':ob['submit_time'],
			'cluster':cluster,
	}
	(job, created)=Job.objects.get_or_create(
			job_id=ob['job_id'],
			cluster=cluster,
			user=user,
			submit_time=ob['submit_time'],
			defaults=jobData
			)
	if ob['type']=='job_new':
		js=JobSubmitInfo()
		js.job=job
		fields=[
			'user_id',
			'options',
			'options2',
			'num_processors',
			'begin_time',
			'term_time',
			'checkpoint_signal_value',
			'checkpoint_period',
			'restart_process_id',
			'host_factor',
			'umask',
			'requested_resources',
			'cwd',
			'checkpoint_dir',
			'input_file',
			'output_file',
			'error_file',
			'input_file_spool',
			'command_spool',
			'job_spool_dir',
			'home_directory',
			'job_file',
			'dependency_conditions',
			'job_name',
			'command',
			'nxf',
			'pre_execution_command',
			'email_user',
			'nios_port',
			'max_num_processors',
			'login_shell',
			'array_index',
			'user_priority',
		]
		for field in fields:
			setattr(js,field,ob[field])
		if len(ob['host_specification_hostname'])<1:
			ob['host_specification_hostname']="Unknown"
		if len(ob['scheduled_host_type'])<1:
			ob['scheduled_host_type']="Unknown"
		(queue, created)=Queue.objects.get_or_create(name=ob['queue'])
		js.queue=queue
		(host,created)=Host.objects.get_or_create(host_name=ob['host_specification_hostname'])
		js.host_specification_hostname=host
		(host,created)=Host.objects.get_or_create(host_name=ob['scheduled_host_type'])
		js.scheduled_host_type=host
		(project, created)=Project.objects.get_or_create(name=ob['project'])
		js.project=project
		try:
			js.save()
		except:
			pass

	elif ob['type']=='job_finish':
		if ob['start_time']<1:
			ob['wall_time']=0
			ob['pend_time']=ob['end_time']-ob['submit_time']
			ob['start_time']=ob['end_time']
		else:
			ob['wall_time']=ob['end_time']-ob['start_time']
			ob['pend_time']=ob['start_time']-ob['submit_time']
		elementData={
				'task_id':ob['array_index'],
				}
		(element, created)=job.elements.get_or_create(task_id=ob['array_index'], defaults=elementData)
		(queue, created)=Queue.objects.get_or_create(name=ob['queue'])
		runData={
				'element':element,
				'job':job,
				'num_processors':ob['num_processors'],
				'start_time':ob['start_time'],
				'end_time':ob['end_time'],
				'wall_time':ob['wall_time'],
				'cpu_time':ob['wall_time']*ob['num_processors'],
				'pend_time':ob['pend_time'],
				'queue':queue,
				}
		(run,created)=Run.objects.get_or_create(job=job, element=element, start_time=ob['start_time'], defaults=runData)
		if created:
			for project_name in ob['projects']:
				(project, created)=Project.objects.get_or_create(name=project_name)
				run.projects.add(project)
			hosts={}
			for host_name in ob['used_hosts']:
				try:
					hosts[host_name]+=1
				except:
					hosts[host_name]=1
			for host_name in hosts.iterkeys():
				(host,created)=Host.objects.get_or_create(host_name=host_name)
				run.executions.create(host=host, run=run, num_processors=hosts[host_name])
			rf=RunFinishInfo()
			rf.run=run
			(js, created)=JobStatus.objects.get_or_create(job_status=ob['job_status'])
			rf.job_status=js
			(ei,created)=ExitReason.objects.get_or_create(name=ob['exit_reason']['name'], defaults={'description':ob['exit_reason']['description'],'value':ob['exit_reason']['value']})
			rf.exit_reason = ei
			fields=[
					'user_name',
					'options',
					'num_processors',
					'begin_time',
					'term_time',
					'requested_resources',
					'cwd',
					'input_file',
					'output_file',
					'error_file',
					'input_file_spool',
					'command_spool',
					'job_file',
					'host_factor',
					'job_name',
					'command',
					'dependency_conditions',
					'pre_execution_command',
					'email_user',
					'max_num_processors',
					'login_shell',
					'max_residual_mem',
					'max_swap',
					]
			for field in fields:
				setattr(rf,field,ob[field])
			rf.project_name='None'
			if len(ob['projects'])>0:
				rf.projecT_name=ob['projects'][0]
			rf.save()
			for host in ob['requested_hosts']:
				(h,created)=Host.objects.get_or_create(host_name=host)
				rf.requested_hosts.add(h)
			for res in ob['resource_usage']:
				r=ResourceUsage()
				r.run=run
				r.timestamp=res['timestamp']
				r.is_summary=res['is_summary']
				r.save()
				for metric in res['metrics']:
					m=ResourceUsageMetric()
					m.resource_usage=r
					m.name=metric['name']
					m.value=metric['value']
					m.description=metric['description']
					m.save()























FRIENDLY_NAMES={
		'cluster':{
			'name':"Cluster",
			'value':Cluster.objects.get,
			},
		'exit_status_code':{
			'name':"Exit Status",
			'value':ExitReason.objects.get,
			},
		'num_processors':{
			'name':'Num Processors',
			},
		'user_name':{
			'name':"User Name",
			'value':User.objects.get,
			},
		'executionHost':{
			'name':"Execution Host",
			'value':Host.objects.get,
			},
		'queue':{
			'name':"Queue",
			'value':Queue.objects.get,
			},
		'project':{
			'name':"Project",
			'value':Project.objects.get,
			},
		}



@cache_page(60 * 15)
def homeView(request,start_time=-1, end_time=-1, filterString=''):
	log.debug(filterString)
	return render_to_response("lavaFlow/homeView.html",{'filters':filterStringToFilterJson(filterString), 'start_time':start_time,'end_time':end_time,'filterString':filterString},context_instance=RequestContext(request))

def filterStringToFilterJson(filterString):
	filters={'filter':{},'exclude':{}}
	if len(filterString) > 0:
		entries=filterString.split("/")
		if len(entries)>0 and len(entries)%3 == 0:
			entries=iter(entries)
			for type,name,value in zip(entries,entries,entries):
				try:
					f=filters[type]
				except KeyError:
					continue
				fValue=value
				try:
					fValue=str(FRIENDLY_NAMES[name]['value'](pk=value))
				except KeyError:
					pass
				try:
					filters[type][name]['values'].append({'value':value,'friendlyValue':fValue})
				except KeyError:
					filters[type][name]={
							'friendlyName':FRIENDLY_NAMES[name]['name'],
							'filterName':name,
							'friendlyValue':fValue,
							'values':[{'value':value,'friendlyValue':fValue}],
							}
	return json.dumps(filters)
## Returns a JSON object with the timestamps from the 
#  first job submitted and last job to exit
#  Times are seconds since Epoch in UTC time.

@cache_page(60 * 15)
def getReportRange(date):
	data={
		'end_time':Run.objects.aggregate(Max('end_time'))['end_time__max'],
		'start_time':Job.objects.aggregate(Min('submit_time'))['submit_time__min'],
	}
	if data['end_time']==None:
		data['end_time']=0

	if data['start_time']==None:
		data['start_time']=0

	return HttpResponse(json.dumps(data), mimetype='application/json')

def filterSet(set,fields,filterString):
	# {filter|exclude}/name/value/
	if len(filterString)==0:
		return set

	exclude={}
	filter={}
	entries=filterString.split("/")
	if len(entries)<1:
		return set
	if len(entries)%3 != 0:
		raise ValueError
	entries=iter(entries)
	
	for type,name,value in zip(entries,entries,entries):
		if type=="filter":
			filter[fields[name]]=value
		elif type=="exclude":
			exclude[fields[name]]=value
		else:
			raise ValueError
	log.debug(filter)
	log.debug(exclude)
	set=set.filter(**filter)
	set=set.exclude(**exclude)
	return set

def filterJobs(jobs,filterString):
	fields={
		'cluster':'cluster',
		'exit_status_code':'runs__runFinishInfo__exit_status_code',
		'num_processors':'runs__num_processors',
		'user_name':'user',
		'executionHost':'runs__executions__host',
		'queue':'runs__queue',
		'project':'runs__project',
		}
	return filterSet(jobs, fields, filterString)
def filterRuns(runs, filterString):
	fields={
		'cluster':'job__cluster',
		'exit_status_code':'runFinishInfo__exit_status_code',
		'num_processors':'num_processors',
		'user_name':'job__user',
		'executionHost':'executions__host',
		'queue':'queue',
		'project':'projects',
		}
	return filterSet(runs,fields,filterString)

ALLOWED_GROUPS={
			'job__cluster__name':{
				'friendlyName':"Cluster",
			},
			'projects__name':{
				'friendlyName':'Project',
			},
			'queue__name':{
				'friendlyName':'Queue',
			},
			'num_processors':{
				'friendlyName':"Num Processors",
			},
			'job__user__user_name':{
				'friendlyName':"User",
			}
		}

@cache_page(60 * 15)
def groupedUtilizationTableModule(request, start_time,end_time,groupString,filterString=''):
	groups=groupString.split("/")
	friendlyNames=[]
	for group in groups:
		if group not in ALLOWED_GROUPS:
			raise Http404( "Group: %s not allowed" % group)
		friendlyNames.append(ALLOWED_GROUPS[group]['friendlyName'])
	
	start_time=int(start_time)
	end_time=int(end_time)
	log.debug(filterString)
	rows=filterRuns(Run.objects.filter(element__job__submit_time__lte=end_time, end_time__gte=start_time),filterString)
	rows=rows.values(*groups).order_by(*groups)
	rows=rows.annotate(
			totalJobs=Count('element__job__id'),
			totalTasks=Count('element__id'),
			totalRuns=Count('id'),
			totalCPUTime=Sum('cpu_time'),
			totalWallTime=Sum('wall_time'),
			totalPend_time=Sum('pend_time'),
		)

	for row in rows:
		r=[]
		for field in groups:
			r.append(row[field])
		row['fields']=r
		row['CPUTime']=datetime.timedelta(seconds=row['totalCPUTime'])
		row['wall_time']=datetime.timedelta(seconds=row['totalWallTime'])
		row['pend_time']=datetime.timedelta(seconds=row['totalPend_time'])
	return render_to_response("lavaFlow/modules/groupedUtilization.html",{'fields':friendlyNames,'rows':rows,},context_instance=RequestContext(request))


@cache_page(60 * 15)
def busyUsersModule(request, start_time, end_time, field, filterString=''):
	ALLOWED_FIELDS=['sumPend','sumWall','sumCpu','avgPend','avgWall','avgCpu','maxPend','maxWall','maxCpu','minPend','minWall','minCpu']
	if field.lstrip('-') not in ALLOWED_FIELDS:
		raise Http404(field)

	users=filterRuns(Run.objects.filter(element__job__submit_time__lte=end_time, end_time__gte=start_time),filterString).values('element__job__user__id').annotate(
			numJobs=Count('element__job__id'),
			numTasks=Count('element__id'),
			numRuns=Count('id'),
			sumPend=Sum('pend_time'),
			sumWall=Sum('wall_time'),
			sumCpu=Sum('cpu_time'),
			avgPend=Avg('pend_time'),
			avgWall=Avg('wall_time'),
			avgCpu=Avg('cpu_time'),
			maxPend=Max('pend_time'),
			maxWall=Max('wall_time'),
			maxCpu=Max('cpu_time'),
			minPend=Min('pend_time'),
			minWall=Min('wall_time'),
			minCpu=Min('cpu_time'),
			).order_by(field)[0:10]
	for u in users:
		for f in [
				'sumPend',
				'sumWall',
				'sumCpu',
				'avgPend',
				'avgWall',
				'avgCpu',
				'maxPend',
				'maxWall',
				'maxCpu',
				'minPend',
				'minWall',
				'minCpu']:
			u[f]=datetime.timedelta(seconds=u[f])
		u['user']=User.objects.get(pk=u['element__job__user__id'])
	return render_to_response("lavaFlow/modules/busyUsers.html",{'users':users},context_instance=RequestContext(request))


@cache_page(60 * 15)
def bestHostModule(request, start_time, end_time, filterString=''):
	hosts=filterRuns(Run.objects.filter(element__job__submit_time__lte=end_time, end_time__gte=start_time, runFinishInfo__job_status__job_status="Done"),filterString).values('executions__host').annotate(
			numRuns=Count('id'),
			sumCpu=Sum('cpu_time'),
		).order_by('-numRuns')[0:10]
	for h in hosts:
		try:
			h['host']=Host.objects.get(pk=h['executions__host'])
		except:
			h['host']='None'
		h['sumCpu']=datetime.timedelta(seconds=h['sumCpu'])
	return render_to_response("lavaFlow/modules/busyHosts.html",{'hosts':hosts},context_instance=RequestContext(request))



@cache_page(60 * 15)
def worstHostModule(request, start_time, end_time,filterString=''):
	hosts=filterRuns(Run.objects.exclude(element__job__submit_time__lte=end_time, end_time__gte=start_time, runFinishInfo__job_status__job_status="Done"),filterString).exclude(executions__host__isnull=True).values('executions__host').annotate(
			numRuns=Count('id'),
			sumCpu=Sum('cpu_time'),
		).order_by('-numRuns')[0:10]
	for h in hosts:
		try:
			h['host']=Host.objects.get(pk=h['executions__host'])
		except:
			h['host']='None'
		h['sumCpu']=datetime.timedelta(seconds=h['sumCpu'])
	return render_to_response("lavaFlow/modules/busyHosts.html",{'hosts':hosts},context_instance=RequestContext(request))


@cache_page(60 * 15)
def busySubmitModule(request, start_time, end_time,filterString=''):
	hosts=filterRuns(Run.objects.filter(element__job__submit_time__lte=end_time, end_time__gte=start_time),filterString).values('element__job__submit_host').annotate(
			numRuns=Count('id'),
			sumCpu=Sum('cpu_time'),
			).order_by('-numRuns')[0:10]
	for h in hosts:
		try:
			h['host']=Host.objects.get(pk=h['element__job__submit_host'])
		except:
			h['host']='None'
		h['sumCpu']=datetime.timedelta(seconds=h['sumCpu'])
	return render_to_response("lavaFlow/modules/busyHosts.html",{'hosts':hosts},context_instance=RequestContext(request))



@cache_page(60 * 15)
def jobSizeChartModule(request, start_time, end_time, filterString=''):
	rows=filterRuns(Run.objects.filter(element__job__submit_time__lte=end_time, end_time__gte=start_time),filterString).values('num_processors').annotate(
			numRuns=Count('num_processors'),
			sumPend_time=Sum('pend_time'),
			sumWallTime=Sum('wall_time'),
			sumCpuTime=Sum('cpu_time'),
			avgPend_time=Sum('pend_time'),
			avgWallTime=Sum('wall_time'),
			avgCpuTime=Sum('cpu_time'),
			minPend_time=Sum('pend_time'),
			minWallTime=Sum('wall_time'),
			minCpuTime=Sum('cpu_time'),
			maxPend_time=Sum('pend_time'),
			maxWallTime=Sum('wall_time'),
			maxCpuTime=Sum('cpu_time'),
		).order_by('num_processors')
	
	values=[]
	for s in [('numRuns','Num Runs'),('sumPend_time','Pend Time'),('sumWallTime','Wall Time'),('sumCpuTime','CPU Time')]:
		key=s[1]
		fname=s[0]
		series={
				'key':key,
				'values':[],
				}
		for i in rows:
			series['values'].append(
				{
					'x': i['num_processors'],
					'y': i[fname],
				})
		values.append(series)
	return HttpResponse(json.dumps(values), mimetype='application/json')



@cache_page(60 * 15)
def jobSizeTableModule(request, start_time, end_time,filterString=''):
	rows=filterRuns(Run.objects.filter(element__job__submit_time__lte=end_time, end_time__gte=start_time),filterString).values('num_processors').annotate(
			numRuns=Count('num_processors'),
			sumPend_time=Sum('pend_time'),
			sumWallTime=Sum('wall_time'),
			sumCpuTime=Sum('cpu_time'),
			avgPend_time=Sum('pend_time'),
			avgWallTime=Sum('wall_time'),
			avgCpuTime=Sum('cpu_time'),
			minPend_time=Sum('pend_time'),
			minWallTime=Sum('wall_time'),
			minCpuTime=Sum('cpu_time'),
			maxPend_time=Sum('pend_time'),
			maxWallTime=Sum('wall_time'),
			maxCpuTime=Sum('cpu_time'),
		).order_by('num_processors')
	for r in rows:
		try:
			f= float((float(r['sumPend_time'])/float(r['sumWallTime']))*100)
			r['pendPct']='%.2f' % f
		except ZeroDivisionError:
			r['pendPct']=100
		r['filterString']="filter/num_processors/%s" % r['num_processors']	
		for f in ['sumPend_time','sumWallTime','sumCpuTime','avgPend_time','avgWallTime','avgCpuTime','minPend_time','minWallTime','minCpuTime','maxPend_time','maxWallTime','maxCpuTime',]:
			r[f]=datetime.timedelta(seconds=r[f])
	return render_to_response("lavaFlow/modules/jobSizeTable.html",{'rows':rows,'start_time':start_time,'end_time':end_time,'filterString':filterString},context_instance=RequestContext(request))


@cache_page(60 * 15)
def jobExitTableModule(request, start_time, end_time,filterString=''):
	info=filterRuns(Run.objects.filter(
				element__job__submit_time__lte=end_time, 
				end_time__gte=start_time
			),filterString).values(
					'runFinishInfo__exit_reason'
			).annotate(
				numRuns=Count('num_processors'),
				sumPend_time=Sum('pend_time'),
				sumWallTime=Sum('wall_time'),
				sumCpuTime=Sum('cpu_time'),
				avgPend_time=Sum('pend_time'),
				avgWallTime=Sum('wall_time'),
				avgCpuTime=Sum('cpu_time'),
				minPend_time=Sum('pend_time'),
				minWallTime=Sum('wall_time'),
				minCpuTime=Sum('cpu_time'),
				maxPend_time=Sum('pend_time'),
				maxWallTime=Sum('wall_time'),
				maxCpuTime=Sum('cpu_time'),
			).order_by('-numRuns')
	for i in info:
		for f in ['sumPend_time','sumWallTime','sumCpuTime','avgPend_time','avgWallTime','avgCpuTime','minPend_time','minWallTime','minCpuTime','maxPend_time','maxWallTime','maxCpuTime',]:
			i[f]=datetime.timedelta(seconds=i[f])
		i['exit']=ExitReason.objects.get(pk=i['runFinishInfo__exit_reason'])
	return render_to_response("lavaFlow/modules/jobExitTable.html",{'rows':info,'start_time':start_time,'end_time':end_time,'filterString':filterString},context_instance=RequestContext(request))


@cache_page(60 * 15)
def jobExitChartModule(request, start_time, end_time,filterString=''):
	rows=filterRuns(Run.objects.filter(
				element__job__submit_time__lte=end_time, 
				end_time__gte=start_time
			),filterString).values(
					'runFinishInfo__exit_reason'
			).annotate(
				numRuns=Count('num_processors'),
				sumPend_time=Sum('pend_time'),
				sumWallTime=Sum('wall_time'),
				sumCpuTime=Sum('cpu_time'),
			).order_by('-numRuns')
	values=[]
	for s in [('numRuns','Num Runs'),('sumPend_time','Pend Time'),('sumWallTime','Wall Time'),('sumCpuTime','CPU Time')]:
		key=s[1]
		fname=s[0]
		series={
				'key':key,
				'values':[],
				}
		for i in rows:
			i['exit']=ExitReason.objects.get(pk=i['runFinishInfo__exit_reason'])
			series['values'].append(
				{
					'x': i['exit'].name,
					'y': i[fname],
				})
		values.append(series)
	return HttpResponse(json.dumps(values), mimetype='application/json')


@cache_page(60 * 15)
def jobListModule(request, start_time, end_time, filterString=''):
	jobs=filterJobs(Job.objects.filter(
			submit_time__lte=end_time, 
			runs__end_time__gte=start_time
	),filterString)
	paginator = Paginator(jobs, 30)
	page = request.GET.get('page')
	if not page:
		page=1
	try:
		jobs=paginator.page(page)
	except PageNotAnInteger:
		jobs=paginator.page(1)
	except EmptyPage:
		jobs= paginator.page(paginator.num_pages)
	return render_to_response("lavaFlow/modules/jobList.html",{'jobs':jobs},context_instance=RequestContext(request))


@cache_page(60 * 15)
def utilizationModule(request, start_time, end_time,filterString=''):
	util=filterRuns(Run.objects.filter(
				element__job__submit_time__lte=end_time, 
				end_time__gte=start_time
			),filterString)
	data=util.utilizationN3DS(start_time, end_time,500,"")
	return HttpResponse(data, mimetype='application/json')


@cache_page(60 * 15)
def groupedUtilizationChartModule(request, start_time, end_time, groupString, filterString=''):
	groups=groupString.split("/")
	util=filterRuns(Run.objects.filter(
				element__job__submit_time__lte=end_time, 
				end_time__gte=start_time
			),filterString)
	for group in groups:
		if group not in ALLOWED_GROUPS:
			raise Http404( "Group: %s not allowed"% group)
	
	data=util.complexUtilization(start_time, end_time,500,groups)
	return HttpResponse(data, mimetype='application/json')

