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
import time
from django.db import models
from django.db.models import Avg, Count, Sum, Min, Max
from django.core.urlresolvers import reverse
from django.core.cache import cache
log=logging.getLogger(__name__)
class OpenLavaState(models.Model):
	code=models.CharField(max_length=50)
	name=models.CharField(max_length=128)
	description=models.TextField()
	friendly_name=models.CharField(max_length=128,null=True)
	class Meta:
		abstract=True

class OpenLavaSubmitOption(OpenLavaState):
	pass
class OpenLavaSubmitOption(OpenLavaState):
	pass
class OpenLavaTransferFileOption(OpenLavaState):
	pass
class JobStatus(OpenLavaState):
	pass


class Cluster(models.Model):
	name=models.CharField(
			max_length=100,
			unique=True,
			db_index=True,
			help_text='The name of the cluster',
			)

	def __unicode__(self):
		return u'%s' % self.name

	def __str__(self):
		return self.name


class Project(models.Model):
	name=models.CharField(max_length=100,unique=True,db_index=True)
	def __unicode__(self):
		return u'%s' % self.name

	def __str__(self):
		return self.name


class Host(models.Model):
	name=models.CharField(max_length=100,db_index=True,unique=True)

	def __unicode__(self):
		return u'%s' % self.name

	def __str__(self):
		return self.name


class Queue(models.Model):
	cluster=models.ForeignKey(Cluster,db_index=True)
	name=models.CharField(max_length=128)

	def __unicode__(self):
		return u'%s' % self.name

	def __str__(self):
		return self.name

	class Meta:
		unique_together=('cluster','name')
		index_together=[
				('cluster','name'),
		]

class User(models.Model):
	name=models.CharField(max_length=128,db_index=True,unique=True)
	def __unicode__(self):
		return u'%s' % self.name
	def __str__(self):
		return '%s' % self.name


class Job(models.Model):
	cluster=models.ForeignKey(Cluster)
	job_id=models.IntegerField()
	user=models.ForeignKey(User)
	submit_host=models.ForeignKey(Host)
	submit_time=models.IntegerField()

	def get_absolute_url(self):
		return reverse('job_detail',args=[self.id])

	def __unicode__(self):
		return u"%s" % self.job_id

	def __str__(self):
		return "%s" % self.job_id

	def submit_time_datetime(self):
		return datetime.datetime.fromtimestamp(self.submit_time)

	def submit_time_datetime(self):
		return datetime.datetime.utcfromtimestamp(self.submit_time)

	class Meta:
		unique_together=('cluster','job_id','submit_time')

		index_together=[
					['cluster','user'],
					['cluster','job_id','submit_time',],
					['cluster','user','submit_time'],
				]

class OpenLavaTransferFile(models.Model):
	submission_file_name=models.CharField(max_length=4096)
	execution_file_name=models.CharField(max_length=4096)
	options=models.ManyToManyField(OpenLavaTransferFileOption)

class OpenLavaResourceLimit(models.Model):
	cpu=models.IntegerField()
	file_size=models.IntegerField()
	data=models.IntegerField()
	stack=models.IntegerField()
	core=models.IntegerField()
	rss=models.IntegerField()
	run=models.IntegerField()
	process=models.IntegerField()
	swap=models.IntegerField()
	nofile=models.IntegerField()
	open_files=models.IntegerField()

class JobSubmitOpenLava(models.Model):
	job=models.OneToOneField(Job)
	user_id=models.IntegerField()
	user=models.ForeignKey(User, db_column="user_rem_id")
	options=models.ManyToManyField(OpenLavaSubmitOption)
	num_processors=models.IntegerField()
	begin_time=models.IntegerField()
	def begin_time_datetime(self):
		return datetime.datetime.utcfromtimestamp(self.begin_time)
	termination_time=models.IntegerField()
	def termination_time_datetime(self):
		return datetime.datetime.utcfromtimestamp(self.termination_time)
	signal_value=models.IntegerField()
	checkpoint_period=models.IntegerField()
	def checkpoint_period_timedelta(self):
		return datetime.timedelta(minutes=self.checkpoint_period)
	restart_pid=models.IntegerField()
	resource_limits=models.OneToOneField(OpenLavaResourceLimit)
	host_specification=models.CharField(max_length=64)
	host_factor=models.FloatField()
	umask=models.IntegerField()
	queue=models.ForeignKey(Queue)
	resource_request=models.TextField()
	submission_host=models.ForeignKey(Host, related_name="submitted_openlava_jobs")
	cwd=models.CharField(max_length=256)
	checkpoint_directory=models.CharField(max_length=256)
	input_file=models.CharField(max_length=256)
	output_file=models.CharField(max_length=256)
	error_file=models.CharField(max_length=256)
	input_file_spool=models.CharField(max_length=256)
	command_spool=models.CharField(max_length=256)
	spool_directory=models.CharField(max_length=4096)
	submission_home_dir=models.CharField(max_length=265)
	job_file=models.CharField(max_length=265)
	asked_hosts=models.ManyToManyField(Host, related_name="requested_by_openlava_jobs")
	dependency_condition=models.CharField(max_length=4096)
	job_name=models.CharField(max_length=512)
	command=models.CharField(max_length=512)
	num_transfer_files=models.IntegerField()
	transfer_files=models.ManyToManyField(OpenLavaTransferFile)
	pre_execution_command=models.TextField()
	email_user=models.CharField(max_length=512)
	project=models.ForeignKey(Project)
	nios_port=models.IntegerField()
	max_num_processors=models.IntegerField()
	schedule_host_type=models.CharField(max_length=1024)
	login_shell=models.CharField(max_length=1024)
	user_priority=models.IntegerField()

class Task(models.Model):
	cluster=models.ForeignKey(Cluster)
	job=models.ForeignKey(Job)
	user=models.ForeignKey(User)
	task_id=models.IntegerField()

	def get_absolute_url(self):
		return reverse('task_detail',args=[self.id])

	def __unicode__(self):
		return u"%s" % self.task_id

	def __str__(self):
		return "%s" % self.task_id

	class Meta:
		index_together=[
				['cluster','job'],
				['cluster','user'],
				['user'],
				]

class Attempt(models.Model):
	cluster=models.ForeignKey(Cluster)
	job=models.ForeignKey(Job)
	task=models.ForeignKey(Task)
	user=models.ForeignKey(User)
	num_processors=models.IntegerField()
	projects=models.ManyToManyField(Project)
	execution_hosts=models.ManyToManyField(Host)
	start_time=models.IntegerField()
	def start_time_datetime(self):
		return datetime.datetime.utcfromtimestamp(self.start_time)
	end_time=models.IntegerField()
	def end_time_datetime(self):
		return datetime.datetime.utcfromtimestamp(self.end_time)
	cpu_time=models.IntegerField()
	def cpu_time_timedelta(self):
		return datetime.timedelta(seconds=self.cpu_time)
	wall_time=models.IntegerField()
	def wall_time_timedelta(self):
		return datetime.timedelta(seconds=self.wall_time)
	pend_time=models.IntegerField()
	def pend_time_timedelta(self):
		return datetime.timedelta(seconds=self.pend_time)
	queue=models.ForeignKey(Queue)
	status=models.ForeignKey(JobStatus)
	command=models.TextField()
	def get_absolute_url(self):
		return reverse('attempt_detail',args=[self.id])
	def get_attempt_id(self):
		counter=1
		for attempt in self.task.attempt_set.all().order_by('start_time'):
			if attempt.id==self.id:
				return counter
			counter+=1

	class Meta:
		unique_together=('cluster','job','task','start_time')
		index_together=[
				('cluster','job','task'),
				('cluster','job','task', 'start_time',),
		]

class OpenLavaResourceUsage(models.Model):
	user_time=models.FloatField()
	system_time=models.FloatField()
	max_rss=models.FloatField()
	integral_rss=models.FloatField()
	integral_shared_memory=models.FloatField()
	integral_unshared_data=models.FloatField()
	integral_unshared_stack=models.FloatField()
	page_reclaims=models.FloatField()
	page_faults=models.FloatField()
	swaps=models.FloatField()
	block_input_operations=models.FloatField()
	block_output_operations=models.FloatField()
	charecter_io=models.FloatField()
	messages_sent=models.FloatField()
	messages_recieved=models.FloatField()
	signals_recieved=models.FloatField()
	voluntary_context_switches=models.FloatField()
	involuntary_context_switches=models.FloatField()
	exact_user_time=models.FloatField()


class OpenLavaExitInfo(models.Model):
	attempt=models.OneToOneField(Attempt)
	user_id=models.IntegerField()
	user=models.ForeignKey(User, db_column="user_rem_id")
	options=models.ManyToManyField(OpenLavaSubmitOption)
	begin_time=models.IntegerField()
	def begin_time_datetime(self):
		return datetime.datetime.utcfromtimestamp(self.begin_time)
	termination_time=models.IntegerField()
	def termination_time_datetime(self):
		return datetime.datetime.utcfromtimestamp(self.termination_time)
	resource_request=models.TextField()
	cwd=models.CharField(max_length=256)
	input_file=models.CharField(max_length=256)
	output_file=models.CharField(max_length=256)
	error_file=models.CharField(max_length=256)
	input_file_spool=models.CharField(max_length=256)
	command_spool=models.CharField(max_length=256)
	job_file=models.CharField(max_length=265)
	asked_hosts=models.ManyToManyField(Host)
	host_factor=models.FloatField()
	job_name=models.CharField(max_length=512)
	resource_usage=models.OneToOneField(OpenLavaResourceUsage)
	dependency_condition=models.CharField(max_length=4096)
	pre_execution_command=models.TextField()
	email_user=models.CharField(max_length=512)
	project=models.ForeignKey(Project)
	exit_status=models.IntegerField()
	max_num_processors=models.IntegerField()
	login_shell=models.CharField(max_length=1024)
	array_index=models.IntegerField()
	max_residual_mem=models.IntegerField()
	max_swap=models.IntegerField()

