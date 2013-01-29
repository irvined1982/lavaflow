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
def renderElementDetail(element):
	return render_to_response('lsf/elementDetailView.html',{'element':element,},context_instance=RequestContext(request))	

def runDetailView(request,id):
	run=get_object_or_404(Run,pk=id)
	return render_to_response('lavaFlow/runDetailView.html',{'run':run},context_instance=RequestContext(request))

def outageView(request, id):
	outage=get_object_or_404(Outage, pk=id)
	return render_to_response('lavaFlow/outageView.html',{'outage':outage},context_instance=RequestContext(request))

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

def hostView(request,id):
	host=get_object_or_404(Host, pk=id)
	return render_to_response('lavaFlow/hostView.html',{'host':host},context_instance=RequestContext(request))

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

def userView(request,id):
	user=get_object_or_404(User,pk=id)
	return render_to_response('lavaFlow/userView.html',{'user':user},context_instance=RequestContext(request))

def jobDetailView(request,id):
	job=get_object_or_404(Job,pk=id)
	return render_to_response('lavaFlow/jobDetailView.html',{'job':job,},context_instance=RequestContext(request))






















def homeView(request,startTime=-1, endTime=-1, filterString=''):
	log.debug(filterString)
	return render_to_response("lavaFlow/homeView.html",{'startTime':startTime,'endTime':endTime,'filterString':filterString},context_instance=RequestContext(request))

## Returns a JSON object with the timestamps from the 
#  first job submitted and last job to exit
#  Times are seconds since Epoch in UTC time.
def getReportRange(date):
	data={
		'endTime':Run.objects.aggregate(Max('endTime'))['endTime__max'],
		'startTime':Job.objects.aggregate(Min('submitTime'))['submitTime__min'],
	}
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
		'numProcessors':'elements__runs__numProcessors',
		'exitStatus':'elements__runs__runFinishInfo__exitStatus',
		}
	return filterSet(jobs, fields, filterString)
def filterRuns(runs, filterString):
	fields={
		'cluster':'element__job__cluster',
		'numProcessors':'numProcessors',
		'exitStatus':'runFinishInfo__exitStatus',
		}
	return filterSet(runs,fields,filterString)


def clusterOverviewModule(request, startTime,endTime,filterString=''):
	startTime=int(startTime)
	endTime=int(endTime)
	log.debug(filterString)
	clusters=filterRuns(Run.objects.filter(element__job__submitTime__lte=endTime, endTime__gte=startTime),filterString).values('element__job__cluster__id').annotate(
			totalJobs=Count('element__job__id'),
			totalElements=Count('element__id'),
			totalRuns=Count('id'),
			totalCPUTime=Sum('cpuTime'),
			totalWallTime=Sum('wallTime'),
			totalPendTime=Sum('pendTime'),
		)
	for cluster in clusters:
		cluster['cluster']=Cluster.objects.get(pk=cluster['element__job__cluster__id'])
		cluster['CPUTime']=datetime.timedelta(seconds=cluster['totalCPUTime'])
		cluster['wallTime']=datetime.timedelta(seconds=cluster['totalWallTime'])
		cluster['pendTime']=datetime.timedelta(seconds=cluster['totalPendTime'])
	log.debug(filterString)
	return render_to_response("lavaFlow/modules/clusterOverview.html",{'clusters':clusters,'startTime':startTime,'endTime':endTime,'filterString':filterString},context_instance=RequestContext(request))

def busyUsersModule(request, startTime, endTime, field, filterString=''):
	ALLOWED_FIELDS=['sumPend','sumWall','sumCpu','avgPend','avgWall','avgCpu','maxPend','maxWall','maxCpu','minPend','minWall','minCpu']
	if field.lstrip('-') not in ALLOWED_FIELDS:
		raise Http404(field)

	users=filterRuns(Run.objects.filter(element__job__submitTime__lte=endTime, endTime__gte=startTime),filterString).values('element__job__user__id').annotate(
			numJobs=Count('element__job__id'),
			numElements=Count('element__id'),
			numRuns=Count('id'),
			sumPend=Sum('pendTime'),
			sumWall=Sum('wallTime'),
			sumCpu=Sum('cpuTime'),
			avgPend=Avg('pendTime'),
			avgWall=Avg('wallTime'),
			avgCpu=Avg('cpuTime'),
			maxPend=Max('pendTime'),
			maxWall=Max('wallTime'),
			maxCpu=Max('cpuTime'),
			minPend=Min('pendTime'),
			minWall=Min('wallTime'),
			minCpu=Min('cpuTime'),
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

def bestHostModule(request, startTime, endTime, filterString=''):
	hosts=filterRuns(Run.objects.filter(element__job__submitTime__lte=endTime, endTime__gte=startTime, runFinishInfo__jStatus__jStatus="Done"),filterString).values('executions__host').annotate(
			numRuns=Count('id'),
			sumCpu=Sum('cpuTime'),
		).order_by('-numRuns')[0:10]
	for h in hosts:
		try:
			h['host']=Host.objects.get(pk=h['executions__host'])
		except:
			h['host']='None'
	return render_to_response("lavaFlow/modules/busyHosts.html",{'hosts':hosts},context_instance=RequestContext(request))


def worstHostModule(request, startTime, endTime,filterString=''):
	hosts=filterRuns(Run.objects.exclude(element__job__submitTime__lte=endTime, endTime__gte=startTime, runFinishInfo__jStatus__jStatus="Done"),filterString).exclude(executions__host__isnull=True).values('executions__host').annotate(
			numRuns=Count('id'),
			sumCpu=Sum('cpuTime'),
		).order_by('-numRuns')[0:10]
	for h in hosts:
		try:
			h['host']=Host.objects.get(pk=h['executions__host'])
		except:
			h['host']='None'
	return render_to_response("lavaFlow/modules/busyHosts.html",{'hosts':hosts},context_instance=RequestContext(request))

def busySubmitModule(request, startTime, endTime,filterString=''):
	hosts=filterRuns(Run.objects.filter(element__job__submitTime__lte=endTime, endTime__gte=startTime),filterString).values('element__job__submitHost').annotate(
			numRuns=Count('id'),
			sumCpu=Sum('cpuTime'),
			).order_by('-numRuns')[0:10]
	for h in hosts:
		try:
			h['host']=Host.objects.get(pk=h['element__job__submitHost'])
		except:
			h['host']='None'
	return render_to_response("lavaFlow/modules/busyHosts.html",{'hosts':hosts},context_instance=RequestContext(request))


def jobSizeChartModule(request, startTime, endTime, filterString=''):
	rows=filterRuns(Run.objects.filter(element__job__submitTime__lte=endTime, endTime__gte=startTime),filterString).values('numProcessors').annotate(
			numRuns=Count('numProcessors'),
			sumPendTime=Sum('pendTime'),
			sumWallTime=Sum('wallTime'),
			sumCpuTime=Sum('cpuTime'),
			avgPendTime=Sum('pendTime'),
			avgWallTime=Sum('wallTime'),
			avgCpuTime=Sum('cpuTime'),
			minPendTime=Sum('pendTime'),
			minWallTime=Sum('wallTime'),
			minCpuTime=Sum('cpuTime'),
			maxPendTime=Sum('pendTime'),
			maxWallTime=Sum('wallTime'),
			maxCpuTime=Sum('cpuTime'),
		).order_by('numProcessors')
	
	values=[]
	for s in [('numRuns','Num Runs'),('sumPendTime','Pend Time'),('sumWallTime','Wall Time'),('sumCpuTime','CPU Time')]:
		key=s[1]
		fname=s[0]
		series={
				'key':key,
				'values':[],
				}
		for i in rows:
			series['values'].append(
				{
					'x': i['numProcessors'],
					'y': i[fname],
				})
		values.append(series)
	return HttpResponse(json.dumps(values), mimetype='application/json')


def jobSizeTableModule(request, startTime, endTime,filterString=''):
	rows=filterRuns(Run.objects.filter(element__job__submitTime__lte=endTime, endTime__gte=startTime),filterString).values('numProcessors').annotate(
			numRuns=Count('numProcessors'),
			sumPendTime=Sum('pendTime'),
			sumWallTime=Sum('wallTime'),
			sumCpuTime=Sum('cpuTime'),
			avgPendTime=Sum('pendTime'),
			avgWallTime=Sum('wallTime'),
			avgCpuTime=Sum('cpuTime'),
			minPendTime=Sum('pendTime'),
			minWallTime=Sum('wallTime'),
			minCpuTime=Sum('cpuTime'),
			maxPendTime=Sum('pendTime'),
			maxWallTime=Sum('wallTime'),
			maxCpuTime=Sum('cpuTime'),
		).order_by('numProcessors')
	for r in rows:
		try:
			f= float((float(r['sumPendTime'])/float(r['sumWallTime']))*100)
			r['pendPct']='%.2f' % f
		except ZeroDivisionError:
			r['pendPct']=100
		r['filterString']="filter/numProcessors/%s" % r['numProcessors']	
		for f in ['sumPendTime','sumWallTime','sumCpuTime','avgPendTime','avgWallTime','avgCpuTime','minPendTime','minWallTime','minCpuTime','maxPendTime','maxWallTime','maxCpuTime',]:
			r[f]=datetime.timedelta(seconds=r[f])
	return render_to_response("lavaFlow/modules/jobSizeTable.html",{'rows':rows,'startTime':startTime,'endTime':endTime,'filterString':filterString},context_instance=RequestContext(request))

def jobExitTableModule(request, startTime, endTime,filterString=''):
	info=filterRuns(Run.objects.filter(
				element__job__submitTime__lte=endTime, 
				endTime__gte=startTime
			),filterString).values(
					'runFinishInfo__exitInfo'
			).annotate(
				numRuns=Count('numProcessors'),
				sumPendTime=Sum('pendTime'),
				sumWallTime=Sum('wallTime'),
				sumCpuTime=Sum('cpuTime'),
				avgPendTime=Sum('pendTime'),
				avgWallTime=Sum('wallTime'),
				avgCpuTime=Sum('cpuTime'),
				minPendTime=Sum('pendTime'),
				minWallTime=Sum('wallTime'),
				minCpuTime=Sum('cpuTime'),
				maxPendTime=Sum('pendTime'),
				maxWallTime=Sum('wallTime'),
				maxCpuTime=Sum('cpuTime'),
			).order_by('-numRuns')
	for i in info:
		for f in ['sumPendTime','sumWallTime','sumCpuTime','avgPendTime','avgWallTime','avgCpuTime','minPendTime','minWallTime','minCpuTime','maxPendTime','maxWallTime','maxCpuTime',]:
			i[f]=datetime.timedelta(seconds=i[f])
		i['exit']=ExitReason.objects.get(pk=i['runFinishInfo__exitInfo'])
	return render_to_response("lavaFlow/modules/jobExitTable.html",{'rows':info,'startTime':startTime,'endTime':endTime,'filterString':filterString},context_instance=RequestContext(request))

def jobExitChartModule(request, startTime, endTime,filterString=''):
	rows=filterRuns(Run.objects.filter(
				element__job__submitTime__lte=endTime, 
				endTime__gte=startTime
			),filterString).values(
					'runFinishInfo__exitInfo'
			).annotate(
				numRuns=Count('numProcessors'),
				sumPendTime=Sum('pendTime'),
				sumWallTime=Sum('wallTime'),
				sumCpuTime=Sum('cpuTime'),
			).order_by('-numRuns')
	values=[]
	for s in [('numRuns','Num Runs'),('sumPendTime','Pend Time'),('sumWallTime','Wall Time'),('sumCpuTime','CPU Time')]:
		key=s[1]
		fname=s[0]
		series={
				'key':key,
				'values':[],
				}
		for i in rows:
			i['exit']=ExitReason.objects.get(pk=i['runFinishInfo__exitInfo'])
			series['values'].append(
				{
					'x': i['exit'].name,
					'y': i[fname],
				})
		values.append(series)
	return HttpResponse(json.dumps(values), mimetype='application/json')

def jobListModule(request, startTime, endTime, filterString=''):
	jobs=filterJobs(Job.objects.filter(
			submitTime__lte=endTime, 
			elements__runs__endTime__gte=startTime
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

def utilizationModule(request, startTime, endTime,filterString=''):
	util=filterRuns(Run.objects.filter(
				element__job__submitTime__lte=endTime, 
				endTime__gte=startTime
			),filterString)
	data=util.utilizationN3DS(startTime, endTime,500,"")
	return HttpResponse(data, mimetype='application/json')

def jobSearchView(request):
	query = request.GET.get('jobid')
	jobs=None
	if query:
		try:
			query=int(query)
			jobs=Job.objects.filter(jobId=query)
		except ValueError:
			pass
	return render_to_response("lavaFlow/jobSearch.html",{'jobs':jobs},context_instance=RequestContext(request))
