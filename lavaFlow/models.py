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
import array
import datetime
import json
import logging
from django.db import models
from django.db.models import Avg, Count, Sum, Min, Max
from django.core.urlresolvers import reverse
from django.core.cache import cache
log=logging.getLogger(__name__)


class QuerySetManager(models.Manager):
	use_for_related_fields = True
	def __init__(self, qs_class=models.query.QuerySet):
		self.queryset_class = qs_class
		super(QuerySetManager, self).__init__()

	def get_query_set(self):
		return self.queryset_class(self.model)

	def __getattr__(self, attr, *args):
		try:
			return getattr(self.__class__, attr, *args)
		except AttributeError:
			return getattr(self.get_query_set(), attr, *args) 


class RunQuerySet(models.query.QuerySet):
	def utilizationN3DS(self, reportStartTime, reportEndTime,maxBlocks,filterString):
		log.debug("TEST")
		blockSize=60 # 60 second block size which will then be downsampled as required.
		reportStartTime=int(int(reportStartTime)/blockSize)*blockSize
		reportEndTime=int(int(reportEndTime)/blockSize)*blockSize
		
		actualBlocks=((reportEndTime-reportStartTime)/blockSize)+1

		running=array.array('l', [0]) * (actualBlocks)
		pending=array.array('l', [0]) * (actualBlocks)

		for run in self.filter(endTime__gte=reportStartTime, startTime__lte=reportEndTime).values('numProcessors','element__job__submitTime','startTime','endTime'):
			cores=run['numProcessors']
			startMinute=int(run['startTime']/blockSize)*blockSize
			endMinute=int(run['endTime']/blockSize)*blockSize
			subMinute=int(run['element__job__submitTime']/blockSize)*blockSize

			if (subMinute<=reportStartTime):
				pending[0]+=cores
			elif (subMinute<=reportEndTime):
				subBlock=int((subMinute-reportStartTime)/blockSize)
				pending[subBlock]+=cores

			if (startMinute<=reportStartTime):
				pending[0]-=cores
				running[0]+=cores
			elif (startMinute<=reportEndTime):
				startBlock=int((startMinute-reportStartTime)/blockSize)
				running[startBlock]+=cores
				pending[startBlock]-=cores

			if (endMinute<=reportEndTime):
				endBlock=int((endMinute-reportStartTime)/blockSize)
				running[endBlock]-=cores
		runningJobs=0
		pendingJobs=0

		for i in range(len(pending)):
			runningJobs+=running[i]
			running[i]=runningJobs
			pendingJobs+=pending[i]
			pending[i]=pendingJobs

		block=reportStartTime
		index=0

		# must downsize, find a slice size that works.:
		sliceSize=int(actualBlocks/maxBlocks)
		if sliceSize<1:
			sliceSize=1

		currentSliceStart=0
		rRunning=[]
		rPending=[]
		while (currentSliceStart<actualBlocks):
			currentSliceEnd=currentSliceStart+sliceSize
			if currentSliceEnd>=actualBlocks:
				currentSliceEnd=actualBlocks-1
				if currentSliceStart==currentSliceEnd:
					break
			sTime=(currentSliceStart*blockSize)+reportStartTime
			p=pending[currentSliceStart:currentSliceEnd]
			r=running[currentSliceStart:currentSliceEnd]

			pval=sum(p)/len(p)
			rval=sum(r)/len(r)
			rPending.append({
					'x':sTime,
					'y':pval,
				})
			rRunning.append({
					'x':sTime,
					'y':rval,
				})
			currentSliceStart+=sliceSize
		data=[
				{
					'key':'Slots In Use',
					'values':rRunning,
				},
				{
					'key':'Slots Requested',
					'values':rPending,
				},
			]
		return json.dumps(data)

class Host(models.Model):
	hostName=models.CharField(max_length=100)
	def get_absolute_url(self):
		return reverse('lavaFlow.views.hostView', args=[self.id,])
	def __unicode__(self):
		return u'%s' % self.hostName
	def __str__(self):
		return self.hostName
	def hostUsage(self):
		info=self.executions.values('run__element__job__cluster','run__queue','run__runFinishInfo__exitInfo').annotate(
				numRuns=Count('run__numProcessors'),
				).order_by('-numRuns')
		for i in info:
			i['cluster']=Cluster.objects.get(pk=i['run__element__job__cluster'])
			i['queue']=Queue.objects.get(pk=i['run__queue'])
			i['exit']=ExitReason.objects.get(pk=i['run__runFinishInfo__exitInfo'])
		return info
	def submittedJobs(self):
		return Job.objects.filter(submitHost=self).count()
	def executedJobs(self):
		return Job.objects.filter(elements__runs__executions__host=self).distinct().count()

	def submitUsage(self):
		info=Run.objects.filter(element__job__submitHost=self).values('element__job__cluster','queue').annotate(
				numJobs=Count('element__job'),
				numElements=Count('element'),
				numRuns=Count('numProcessors'),
				cpuTime=Sum('cpuTime'),
				wallTime=Sum('wallTime'),
				)
		for i in info:
			i['cluster']=Cluster.objects.get(pk=i['element__job__cluster'])
			i['queue']=Queue.objects.get(pk=i['queue'])
			i['cpuTime']=datetime.timedelta(seconds=i['cpuTime'])
			i['wallTime']=datetime.timedelta(seconds=i['wallTime'])
		return info

class Outage(models.Model):
	service=models.CharField(max_length=512)
	startTime=models.IntegerField()
	endTime=models.IntegerField()
	duration=models.IntegerField()
	host=models.ForeignKey(Host, related_name='outages')
	def get_absolute_url(self):
		return '/lavaFlow/outageView/%s/' % self.id
	def durationDelta(self):
		return datetime.timedelta(seconds=self.duration)
	def startTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.startTime)
	def endTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.endTime)
	def runList(self):
		return Run.objects.filter(startTime__gte=self.startTime, endTime__lte=self.endTime).filter(executions__host=self.host)
	def impactedRuns(self):
		return self.runList().count()



class OutageLog(models.Model):
	time=models.IntegerField()
	message=models.TextField()
	outage=models.ForeignKey(Outage, related_name="logEntries")
	def timeDT(self):
		return datetime.datetime.utcfromtimestamp(self.time)


# Create your models here.
class ExitReason(models.Model):
	name=models.CharField(max_length=100)
	description=models.CharField(max_length=1024)
	value=models.IntegerField()
	def __unicode__(self):
		return u'%s' % self.name
	def __str__(self):
		return self.name
		
	def get_filter_string(self):
		return 'filter/exitStatus/%s' % self.id



class JobStatus(models.Model):
    jStatus=models.CharField(max_length=100)

class Cluster(models.Model):
	name=models.CharField(max_length=100)
	def __unicode__(self):
		return u'%s' % self.name
	def __str__(self):
		return self.name
	def get_absolute_url(self):
		endTime=self.lastJobExit()
		firstTime=self.firstSubmitTime()
		startTime=endTime-(7*24*60*60)
		if startTime<firstTime:
			startTime=firstTime
		return reverse('lavaFlow.views.homeView', args=[startTime,endTime,self.get_filter_string()])
	def get_filter_string(self):
		return 'filter/cluster/%s' % self.id
	def firstSubmitTime(self):
		time=cache.get('cluster_firstSubmitTime_%s' %self.id )
		if time:
			log.debug("firstSubmitTime: Read time from cache")
			return time
		else:
			time=Job.objects.filter(cluster=self).aggregate(Min('submitTime'))['submitTime__min']
			log.debug("firstSubmitTime: Writing time to cache")
			cache.set('cluster_firstSubmitTime_%s' %self.id, time, 360)
			return time
	def lastJobExit(self):
		time=cache.get('cluster_lastJobExit_%s' %self.id )
		if time:
			log.debug("lastJobExit: Read time from cache")
			return time
		else:
			time=Run.objects.filter(element__job__cluster=self).aggregate(Max('endTime'))['endTime__max']
			log.debug("lastJobExit: Writing time to cache")
			cache.set('cluster_lastJobExit_%s' %self.id, time, 360)
			return time
			
	def lastJobExitDT(self):
		return datetime.datetime.utcfromtimestamp(self.lastJobExit())
	def firstSubmitTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.firstSubmitTime())

	def userStats(self,field):
		users=self.jobs.values('user').annotate(
				numJobs=Count('jobId'),
				numElements=Count('elements'),
				numRuns=Count('elements__runs'),
				sumPend=Sum('elements__runs__pendTime'),
				sumWall=Sum('elements__runs__wallTime'),
				sumCpu=Sum('elements__runs__cpuTime'),
				avgPend=Avg('elements__runs__pendTime'),
				avgWall=Avg('elements__runs__wallTime'),
				avgCpu=Avg('elements__runs__cpuTime'),
				maxPend=Max('elements__runs__pendTime'),
				maxWall=Max('elements__runs__wallTime'),
				maxCpu=Max('elements__runs__cpuTime'),
				minPend=Min('elements__runs__pendTime'),
				minWall=Min('elements__runs__wallTime'),
				minCpu=Min('elements__runs__cpuTime'),
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
			u['user']=User.objects.get(pk=u['user'])
		return users
	def busyUsers(self):
		return self.userStats('-sumCpu')
	def patientUsers(self):
		return self.userStats('-avgPend')

	def hostStats(self,order):
		hosts=self.jobs.values('elements__runs__executions__host').annotate(
				numRuns=Count('elements__runs')
				).order_by(order)[0:10]
		for h in hosts:
			try:
				h['host']=Host.objects.get(pk=h['elements__runs__executions__host'])
			except:
				h['host']='None'
		return hosts
	def busyHosts(self):
		return self.hostStats('-numRuns')

	def failedHosts(self):
		hosts=self.jobs.exclude(elements__runs__runFinishInfo__jStatus__jStatus="Done").values('elements__runs__executions__host').annotate(
				numRuns=Count('elements__runs')
				).order_by('-numRuns')[0:10]
		for h in hosts:
			try:
				h['host']=Host.objects.get(pk=h['elements__runs__executions__host'])
			except:
				h['host']='None'

		return hosts
		
	def goodHosts(self):
		hosts=self.jobs.filter(elements__runs__runFinishInfo__jStatus__jStatus="Done").values('elements__runs__executions__host').annotate(
				numRuns=Count('elements__runs')
				).order_by('-numRuns')[0:10]
		for h in hosts:
			try:
				h['host']=Host.objects.get(pk=h['elements__runs__executions__host'])
			except:
				h['host']='None'
		return hosts
		
	def busySubmitHosts(self):
		hosts=self.jobs.values('submitHost').annotate(
				numRuns=Count('jobId')
				).order_by('-numRuns')[0:10]
		for h in hosts:
			try:
				h['host']=Host.objects.get(pk=h['submitHost'])
			except:
				h['host']='None'
		return hosts
	def totalJobs(self):
		return self.jobs.count()

	def totalElements(self):
		return Element.objects.filter(job__cluster=self).count()
	def totalRuns(self):
		return Run.objects.filter(element__job__cluster=self).count()
	def cpuTime(self):
		return Run.objects.filter(element__job__cluster=self).aggregate(Sum('cpuTime'))['cpuTime__sum']
	def cpuTimeDelta(self):
		return datetime.timedelta(seconds=self.cpuTime())
	def wallTime(self):
		return Run.objects.filter(element__job__cluster=self).aggregate(Sum('wallTime'))['wallTime__sum']
	def wallTimeDelta(self):
		return datetime.timedelta(seconds=self.wallTime())
	def pendTime(self):
		return Run.objects.filter(element__job__cluster=self).aggregate(Sum('pendTime'))['pendTime__sum']
	def pendTimeDelta(self):
		return datetime.timedelta(seconds=self.pendTime())

class Project(models.Model):
	name=models.CharField(max_length=100)
	cluster=models.ForeignKey(Cluster, related_name='project')
	def get_absolute_url(self):
		return '/lavaFlow/projectView/%s/' % self.id
	def submitUsage(self):
		info=self.runs.values('element__job__cluster','element__job__user','queue','numProcessors').annotate(
				numJobs=Count('element__job'),
				numElements=Count('element'),
				numRuns=Count('numProcessors'),
				cpu=Sum('cpuTime'),
				wall=Sum('wallTime'),
				pend=Sum('pendTime'),
				avgCpu=Avg('cpuTime'),
				avgWall=Avg('wallTime'),
				avgPend=Avg('pendTime'),
				).order_by('element__job__cluster','element__job__user','queue','numProcessors')
		for i in info:
			i['cluster']=Cluster.objects.get(pk=i['element__job__cluster'])
			i['user']=User.objects.get(pk=i['element__job__user'])
			i['queue']=Queue.objects.get(pk=i['queue'])
			i['cpuTime']=datetime.timedelta(seconds=i['cpu'])
			i['wallTime']=datetime.timedelta(seconds=i['wall'])
			i['pendTime']=datetime.timedelta(seconds=i['pend'])
			i['avgWall']=datetime.timedelta(seconds=i['avgWall'])
			i['avgPend']=datetime.timedelta(seconds=i['avgPend'])
			i['avgCpu']=datetime.timedelta(seconds=i['avgCpu'])
		return info

class User(models.Model):
	userName=models.CharField(max_length=128)
	def __unicode__(self):
		return u'%s' % self.userName
	def get_absolute_url(self):
		return reverse('lavaFlow.views.userView', args=[self.id,])
	def submitUsage(self):
		info=Run.objects.filter(element__job__user=self).values('element__job__cluster','queue','numProcessors').annotate(
				numJobs=Count('element__job'),
				numElements=Count('element'),
				numRuns=Count('numProcessors'),
				cpu=Sum('cpuTime'),
				wall=Sum('wallTime'),
				pend=Sum('pendTime'),
				avgCpu=Avg('cpuTime'),
				avgWall=Avg('wallTime'),
				avgPend=Avg('pendTime'),

				)
		for i in info:
			i['cluster']=Cluster.objects.get(pk=i['element__job__cluster'])
			i['queue']=Queue.objects.get(pk=i['queue'])
			i['cpuTime']=datetime.timedelta(seconds=i['cpu'])
			i['wallTime']=datetime.timedelta(seconds=i['wall'])
			i['pendTime']=datetime.timedelta(seconds=i['pend'])
			i['avgWall']=datetime.timedelta(seconds=i['avgWall'])
			i['avgPend']=datetime.timedelta(seconds=i['avgPend'])
			i['avgCpu']=datetime.timedelta(seconds=i['avgCpu'])
		return info

	def runs(self):
		runs=Run.objects.filter(element__job__user=self)
		return runs


class Queue(models.Model):
	name=models.CharField(max_length=128)
	def __unicode__(self):
		return u'%s' % self.name
	def __str__(self):
		return self.name




class JobQuerySet(models.query.QuerySet):
	def uniqClusters(self):
		return self.values('cluster__name').distinct().count()

	def uniqUsers(self):
		return self.values('user__userName').distinct().count()

	def wallTime(self):
		return self.aggregate(Sum('elements__runs__wallTime'))['elements__runs__wallTime__sum']

	def wallTimeDelta(self):
		return datetime.timedelta(seconds=self.wallTime())

	def pendTime(self):
		return self.aggregate(Sum('elements__runs__pendTime'))['elements__runs__pendTime__sum']

	def pendTimeDelta(self):
		return datetime.timedelta(seconds=self.pendTime())

	def cpuTime(self):
		return self.aggregate(Sum('elements__runs__cpuTime'))['elements__runs__cpuTime__sum']

	def cpuTimeDelta(self):
		return datetime.timedelta(seconds=self.cpuTime())

class Job(models.Model):
	objects=QuerySetManager(JobQuerySet)
	jobId=models.IntegerField()
	cluster=models.ForeignKey(Cluster, related_name='jobs')
	user=models.ForeignKey(User, related_name='jobs')
	submitHost=models.ForeignKey(Host, related_name='submitted_jobs')
	submitTime=models.IntegerField()
	def get_absolute_url(self):
		return reverse('lavaFlow.views.jobDetailView', args=[self.id,])

	def wallTime(self):
		return self.elements.aggregate(Sum('runs__wallTime'))['runs__wallTime__sum']
	def wallTimeDelta(self):
		return datetime.timedelta(seconds=self.wallTime())

	def pendTime(self):
		return self.elements.aggregate(Sum('runs__pendTime'))['runs__pendTime__sum']
	def pendTimeDelta(self):
		return datetime.timedelta(seconds=self.pendTime())

	def cpuTime(self):
		return self.elements.aggregate(Sum('runs__cpuTime'))['runs__cpuTime__sum']

	def cpuTimeDelta(self):
		return datetime.timedelta(seconds=self.cpuTime())

	def submitTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.submitTime)

	def firstStartTime(self):
		return self.elements.aggregate(Min('runs__startTime'))['runs__startTime__min']
	def firstStartTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.firstStartTime())

	def lastFinishTime(self):
		return self.elements.aggregate(Max('runs__endTime'))['runs__endTime__max']
	def lastFinishTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.lastFinishTime())

	def firstRun(self):
		return self.elements.order_by('runs__startTime')[0].runs.order_by('startTime')[0]
	def utilizationN3DS(self):
		runs=Run.objects.filter(element__job=self)
		return runs.utilizationN3DS(self.submitTime, self.lastFinishTime(),100, "")

class Element(models.Model):
	elementId=models.IntegerField()
	job=models.ForeignKey(Job, related_name='elements')


class Run(models.Model):
	objects = QuerySetManager(RunQuerySet)
	element=models.ForeignKey(Element, related_name='runs')
	numProcessors=models.IntegerField()
	projects=models.ManyToManyField(Project, related_name='runs')
	startTime=models.IntegerField()
	endTime=models.IntegerField()
	cpuTime=models.IntegerField()
	wallTime=models.IntegerField()
	pendTime=models.IntegerField()
	queue=models.ForeignKey(Queue, related_name='runs')
	def otherRuns(self):
		hosts=self.executions.values('host').distinct()
		runs=Run.objects.filter(startTime__gte=self.startTime, startTime__lte=self.endTime).filter(endTime__gte=self.endTime).filter(executions__host__in=self.executions.values('host').distinct()).exclude(pk=self.id).distinct()
		return runs
	def pendTimeDelta(self):
		return datetime.timedelta(seconds=self.pendTime)
	def wallTimeDelta(self):
		return datetime.timedelta(seconds=self.wallTime)
	def cpuTimeDelta(self):
		return datetime.timedelta(seconds=self.cpuTime)
	def startTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.startTime)

	def endTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.endTime)

	def get_absolute_url(self):
		return reverse("lavaFlow.views.runDetailView", args=[self.id,])

	def utilizationN3DS(self):
		runs=Run.objects.filter(pk=self.id)
		return runs.utilizationN3DS(self.element.job.submitTime, self.endTime,100, "")

class ExecutionHost(models.Model):
	host=models.ForeignKey(Host, related_name="executions")
	run=models.ForeignKey(Run, related_name="executions")
	numProcessors=models.IntegerField()

class RunFinishInfo(models.Model):
    run=models.OneToOneField(
                             Run,
                             related_name='runFinishInfo',
                             help_text="The run associated with the accountin info"
                             )
    options=models.IntegerField(
                                verbose_name="Options 1",
                                help_text="Bit flags for job processing"
                                )
    numProcessors=models.IntegerField(
                                      verbose_name="Processors Used",
                                      help_text="Number of processors initially requested for execution"
                                      )
    beginTime=models.IntegerField(
                                  verbose_name="Begin Time",
                                  help_text="Job start time - the job should be started at or after this time"
                                  )
    termTime=models.IntegerField(
                                 verbose_name="Termination Deadline",
                                 help_text="Job termination deadline - the job should be terminated by this time"
                                 )
    userName=models.CharField(
                              max_length=50,
                              verbose_name="User Name", 
                              help_text="User name of the submitter"
                              )
    resReq=models.TextField(
                            verbose_name="Resource Request",
                            help_text="Resource requirement specified by the user"
                            )
    dependCond=models.TextField(
                                verbose_name="Dependancy Conditions",
                                help_text="Job dependency condition specified by the user"
                                )
    preExecCmd=models.TextField(
                                verbose_name="Pre Execution Command",
                                help_text="Pre-execution command specified by the user"
                                )

    cwd=models.TextField(
                         verbose_name="Curent Working Directory",
                         help_text="Current working directory (up to 4094 characters for UNIX or 255 characters for Windows)"
                         )
    inFile=models.TextField(
                            verbose_name="Input File",
                            help_text="Input file name (up to 4094 characters for UNIX or 255 characters for Windows)"
                            )
    outFile=models.TextField(
                             verbose_name="Output File",
                             help_text="output file name (up to 4094 characters for UNIX or 255 characters for Windows)"
                             )
    errFile=models.TextField(
                             verbose_name="Error File",
                             help_text="Error output file name (up to 4094 characters for UNIX or 255 characters for Windows)"
                             )
    jobFile=models.TextField(
                             verbose_name="Job File",
                             help_text="Job script file name"
                             )
    askedHosts=models.ManyToManyField(Host)
    jStatus=models.ForeignKey(JobStatus)
    hostFactor=models.FloatField(
                                 verbose_name="Host Factor",
                                 help_text="CPU factor of the first execution host"
                                 )
    jobName=models.TextField(
                             verbose_name="Job Name",
                             help_text="Job name (up to 4094 characters for UNIX or 255 characters for Windows)"
                             )
    command=models.TextField(
                             verbose_name="Command",
                             help_text="Complete batch job command specified by the user (up to 4094 characters for UNIX or 255 characters for Windows)"
                             )
    utime=models.FloatField(
                            verbose_name="User Time User",
                            help_text="User time used",
                            )
    stime=models.FloatField(
                            verbose_name="System Time Used",
                            help_text="System time used",
                            )

    maxrss=models.FloatField(
                             verbose_name="Max Shared Text Size",
                             help_text="Maximum shared text size",
                             )
    ixrss=models.FloatField(
                            verbose_name="Integral Shared Text Size",
                            help_text="Integral of the shared text size over time (in KB seconds)",
                            )
    ismrss=models.FloatField(
                             verbose_name="Integral Shmem Size",
                             help_text="Integral of the shared memory size over time (valid only on Ultrix)",
                             )
    idrss=models.FloatField(
                            verbose_name="Integral Data Size",
                            help_text="Integral of the unshared data size over time",
                            )
    isrss=models.FloatField(
                            verbose_name="Integral Stack Size",
                            help_text="Integral of the unshared stack size over time",
                            )
    minflt=models.FloatField(
                             verbose_name="Page Reclaims",
                             help_text="Number of page reclaims",
                             )
    majflt=models.FloatField(
                             verbose_name="Page Faults",
                             help_text="Number of page faults",
                             )
    nswap=models.FloatField(
                            verbose_name="Swapped",
                            help_text="Number of times the process was swapped out",
                            )
    inblock=models.FloatField(
                              verbose_name="Blocks Input",
                              help_text="Number of block input operations",
                              )
    oublock=models.FloatField(
                              verbose_name="Blocks Output",
                              help_text="Number of block output operations",
                              )
    ioch=models.FloatField(
                           verbose_name="Characters Read and Written",
                           help_text="Number of characters read and written (valid only on HP-UX)",
                           )
    msgsnd=models.FloatField(
                             verbose_name="Messages Sent",
                             help_text="Number of System V IPC messages sent",)
    msgrcv=models.FloatField(
                             verbose_name="Messages Recieved",
                             help_text="Number of messages received",
                             )
    nsignals=models.FloatField(
                               verbose_name="Signals Received",
                               help_text="Number of signals received",
                               )
    nvcsw=models.FloatField(
                            verbose_name="Voluntary Context Switches",
                            help_text="Number of voluntary context switches",
                            )

    nivcsw=models.FloatField(
                             verbose_name="Involuntary Context Switches",
                             help_text="Number of involuntary context switches",
                             )
    exutime=models.FloatField(
                              verbose_name="Exact User Time",
                              help_text="Exact user time used (valid only on ConvexOS)",
                              )
    mailUser=models.CharField(
                              max_length=50,
                              verbose_name="Mail User",
                              help_text="Name of the user to whom job related mail was sent"
                              )
    projectName=models.CharField(
                                 max_length=128,
                                 verbose_name="Project Name",
                                 help_text="LSF project name"
                                 )
    exitStatus=models.IntegerField(
                                   verbose_name="Exit Status",
                                   help_text="UNIX exit status of the job"
                                   )
    maxNumProcessors=models.IntegerField(
                                         verbose_name="Max Processors",
                                         help_text="Maximum number of processors specified for the job"
                                         )
    loginShell=models.CharField(
                                max_length=50,
                                verbose_name="Login Shell",
                                help_text="Login shell used for the job"
                                )
    timeEvent=models.CharField(
                               max_length=50,
                               verbose_name="Time Event",
                               help_text="Time event string for the job - JobScheduler only"
                               )
    idx=models.IntegerField(
                            verbose_name="Array Index",
                            help_text="Job array index"
                            )
    maxRMem=models.IntegerField(
                                verbose_name="Max Residual Memory",
                                help_text="Maximum resident memory usage in KB of all processes in the job"
                                )

    maxRSwap=models.IntegerField(
                                 verbose_name="Max Swap Usage",
                                 help_text="Maximum virtual memory usage in KB of all processes in the job"
                                 )    
    inFileSpool=models.TextField(
                                 verbose_name="Input File Spool",
                                 help_text="Spool input file (up to 4094 characters for UNIX or 255 characters for Windows)"
                                 )
    commandSpool=models.TextField(
                                  verbose_name="Command Spool File",
                                  help_text="Spool command file (up to 4094 characters for UNIX or 255 characters for Windows)"
                                  )
    rsvId=models.CharField(
                            max_length=25,
                            verbose_name="Advance reservation ID",
                            help_text="Advance reservation ID"
                            )

    sla=models.CharField(
                         max_length=25,
                         verbose_name="SLA",
                         help_text="SLA service class name under which the job runs"
                         )
        

    exceptMask=models.IntegerField(
                                   verbose_name="Exception Mask",
                                   help_text="Job Exception Mask"
                                   )
    additionalInfo=models.TextField(
                                    verbose_name="Additional Information",
                                    help_text="Placement information of HPC jobs"
                                    )
    exitInfo=models.ForeignKey(ExitReason)                                 
    warningTimePeriod=models.IntegerField(
                                          verbose_name="Warning Time Period",
                                          help_text="Job warning time period in seconds"
                                          )
    warningAction=models.CharField(
                                   max_length=128,
                                   verbose_name="Warning action",
                                   help_text="Job warning action"
                                   )
    
    def contentionChartN3DS(self):
		data=[{
			'key':"System and User time consumed",
			'values':[
				{
					'label':'System Time',
					'value':self.stime,
				},
				{
					'label':'User Time',
					'value':self.utime,
				},
				],
			},]
		return json.dumps(data)

    def resourceUsageChartN3DS(self):
		data=[{
				'key':"Recorded Resource Usage",
				'values':[
					{
						"label": 'Max RSS',
						"value": self.maxrss,
					},
					{
						"label": 'IX RSS'  ,
						"value":  self.ixrss ,
					},
					{
						"label":'ISM RSS'   ,
						"value":self.ismrss   ,
					},
					{
						"label":'ID RSS'   ,
						"value":self.idrss   ,
					},
					{
						"label": "ISRSS"  ,
						"value": self.isrss  ,
					},
					{
						"label": "MINFLT"  ,
						"value": self.minflt  ,
					},
					{
						"label": "MAJFLT",
						"value": self.majflt,
					},
					{
						"label": "NSWAP",
						"value": self.nswap,
					},
					{
						"label": "INBLOCK",
						"value": self.inblock,
					},
					{
						"label": "OUBLOCK",
						"value": self.oublock,
					},
					{
						"label": "IOCH",
						"value": self.ioch,
					},
					{
						"label": "MSGSND",
						"value": self.msgsnd,
					},
					{
						"label": "NSIGNALS",
						"value": self.nsignals,
					},
					{
						"label": "NVCSW",
						"value": self.nvcsw,
					},
					],
			}]
		return json.dumps(data)

class JobSubmitInfo(models.Model):
	job=models.OneToOneField(Job, related_name='jobSubmitInfo',help_text="The Job Associated with the Event")
	submitTime=models.IntegerField()
	def submitTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.submitTime)
	beginTime=models.IntegerField()
	def beginTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.beginTime)
	termTime=models.IntegerField()
	def termTimeDT(self):
		return datetime.datetime.utcfromtimestamp(self.beginTime)

	numProcessors=models.IntegerField()
	sigValue=models.IntegerField()
	chkpntPeriod=models.IntegerField()
	restartPid=models.IntegerField()
	hostSpec=models.TextField()
	hostFactor=models.FloatField()
	umask=models.IntegerField()
	queue=models.ForeignKey(Queue, related_name='jobSubmitInfo')
	resReq=models.TextField()
	submitHost=models.ForeignKey(Host, related_name="jobSubmitInfo")
	cwd=models.TextField()
	chkpntDir=models.TextField()
	inFile=models.TextField()
	outFile=models.TextField()
	errFile=models.TextField()
	inFileSpool=models.TextField()
	commandSpool=models.TextField()
	jobSpoolDir=models.TextField()
	subHomeDir=models.TextField()
	jobFile=models.TextField()
	askedHosts=models.ManyToManyField(Host)
	dependCond=models.TextField()
	timeEvent=models.TextField()
	jobName=models.TextField()
	command=models.TextField()
	preExecCmd=models.TextField()
	mailUser=models.TextField()
	project=models.ForeignKey(Project)
	schedHostType=models.TextField()
	loginShell=models.TextField()
	userGroup=models.TextField()
	exceptList=models.TextField()
	rsvId=models.TextField()
