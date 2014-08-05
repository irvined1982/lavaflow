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
import datetime
import logging
import time
from django.db import models
from django.db.models import Avg, Count, Sum, Min, Max
from django.core.urlresolvers import reverse
from django.core.cache import cache

log = logging.getLogger(__name__)


class ImportKey(models.Model):
    """Any client that attempts to import data must present a valid key. Keys in general should be managed through the
    admin control panel.::

    >>> from lavaFlow.models import ImportKey
    >>> try:
    >>>     key=ImportKey.objects.get(client_key="key_to_check")
    >>>     # Key is valid.
    >>> except ObjectDoesNotExist as e:
    >>>     # Key is invalid.

    .. py:attribute:: client_key

        The Client Key, used by each uploader to authenticate.  This is very rudimentary.

    .. py:attribute:: comment

        Optional comment/description field, free form, example might include which servers/clusters are using this key.
        Not used in any way for authentication.

    """
    client_key = models.CharField(max_length=255, primary_key=True, help_text="Client key, passed by the client to authenticate")
    comment = models.TextField(default="", blank=True, help_text=("Optional description/comment."))

    def __str__(self):
        """
        Returns a str containing the client key.

        :return: str(client_key)

        """
        return str(self.client_key)

    def __unicode__(self):
        """
        Returns the unicode represenation of the client_key

        :return: unicode(client_key)

        """
        return u"%s" % self.__str__()



class OpenLavaState(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=128)
    description = models.TextField()
    friendly_name = models.CharField(max_length=128, null=True)

    @classmethod
    def get_status_list(cls, mask):
        statuses = []
        for key in cls.states.keys():
            if (key & mask) == key:
                statuses.append(cls.states[key])
        return statuses

    class Meta:
        abstract = True
        index_together = [
            ('code', 'name',),
        ]



class OpenLavaSubmitOption(OpenLavaState):
        states = {
        0x01: {
            'code':0x01,
            'name': 'SUB_JOB_NAME',
            'description': "Submitted with a job name",
        },
        0x02: {
            'code': 0x02,
            'name': 'SUB_QUEUE',
            'description': "Job submitted with queue",
        },
        0x04: {
            'code': 0x04,
            'name': 'SUB_HOST',
            'description': "SUB_HOST",
        },
        0x08: {
            'code': 0x08,
            'name': 'SUB_IN_FILE',
            'description': "Job Submitted with input file",
        },
        0x10: {
            'code': 0x10,
            'name': 'SUB_OUT_FILE',
            'description': "Job submitted with output file",
        },
        0x20: {
            'code': 0x20,
            'name': 'SUB_ERR_FILE',
            'description': "Job submitted with error file",
        },
        0x40: {
            'code': 0x40,
            'name': 'SUB_EXCLUSIVE',
            'description': "Job submitted to run exclusively",
        },
        0x80: {
            'code': 0x80,
            'name': 'SUB_NOTIFY_END',
            'description': "SUB_NOTIFY_END",
        },
        0x100: {
            'code': 0x100,
            'name': 'SUB_NOTIFY_BEGIN',
            'description': "SUB_NOTIFY_BEGIN",
        },
        0x200: {
            'code': 0x200,
            'name': 'SUB_USER_GROUP',
            'description': "SUB_USER_GROUP",
        },
        0x400: {
            'code': 0x400,
            'name': 'SUB_CHKPNT_PERIOD',
            'description': "Job submitted with checkpoint period",
        },
        0x800: {
            'code': 0x800,
            'name': 'SUB_CHKPNT_DIR',
            'description': "Job submitted with checkpoint directory",
        },
        0x1000: {
            'code': 0x1000,
            'name': 'SUB_RESTART_FORCE',
            'description': "SUB_RESTART_FORCE",
        },
        0x2000: {
            'code': 0x2000,
            'name': 'SUB_RESTART',
            'description': "SUB_RESTART",
        },
        0x4000: {
            'code': 0x4000,
            'name': 'SUB_RERUNNABLE',
            'description': "Job submitted as rerunnable",
        },
        0x8000: {
            'code': 0x8000,
            'name': 'SUB_WINDOW_SIG',
            'description': "SUB_WINDOW_SIG",
        },
        0x10000: {
            'code': 0x10000,
            'name': 'SUB_HOST_SPEC',
            'description': "Job submitted with host spec",
        },
        0x20000: {
            'code': 0x20000,
            'name': 'SUB_DEPEND_COND',
            'description': "Job submitted with depend conditions",
        },
        0x40000: {
            'code': 0x40000,
            'name': 'SUB_RES_REQ',
            'description': "Job submitted with resource request",
        },
        0x80000: {
            'code': 0x80000,
            'name': 'SUB_OTHER_FILES',
            'description': "SUB_OTHER_FILES",
        },
        0x100000: {
            'code': 0x100000,
            'name': 'SUB_PRE_EXEC',
            'description': "Job submitted with pre exec script",
        },
        0x200000: {
            'code': 0x200000,
            'name': 'SUB_LOGIN_SHELL',
            'description': "Job submitted with login shell",
        },
        0x400000: {
            'code': 0x400000,
            'name': 'SUB_MAIL_USER',
            'description': "Job submitted to email user",
        },
        0x800000: {
            'code': 0x800000,
            'name': 'SUB_MODIFY',
            'description': "SUB_MODIFY",
        },
        0x1000000: {
            'code': 0x1000000,
            'name': 'SUB_MODIFY_ONCE',
            'description': "SUB_MODIFY_ONCE",
        },
        0x2000000: {
            'code': 0x2000000,
            'name': 'SUB_PROJECT_NAME',
            'description': "Job submitted to project",
        },
        0x4000000: {
            'code': 0x4000000,
            'name': 'SUB_INTERACTIVE',
            'description': "Job submitted as interactive",
        },
        0x8000000: {
            'code': 0x8000000,
            'name': 'SUB_PTY',
            'description': "SUB_PTY",
        },
        0x10000000: {
            'code': 0x10000000,
            'name': 'SUB_PTY_SHELL',
            'description': "SUB_PTY_SHELL",
        },
    }


class OpenLavaTransferFileOption(OpenLavaState):
    pass


class JobStatus(OpenLavaState):
    exited_cleanly = models.BooleanField()

    class Meta:
        index_together = [
            ('code', 'name', 'exited_cleanly')
        ]


class Cluster(models.Model):
    """

    Almost every bit of data stored in lavaFlow can be traced back to a cluster, clusters represent the physical compute
    clusters that jobs are executed on.  There could be just one, for a simple departmental cluster, or many for an
    entire organization with both regional and centralized compute services.  Cluster objects are generally created
    automatically by the agents monitoring the cluster.  Extended information is generally added by the end user via
    the admin interface.::

    >>> from lavaFlow.models import Cluster
    >>> (cluster, created) = Cluster.objects.get_or_create(name="openlava")
    >>> cluster.name
    u'openlava'
    >>> cluster.total_attempts()
    9000
    >>> cluster.first_task()
    <Attempt: Attempt object>
    >>> cluster.last_task()
    <Attempt: Attempt object>
    >>> cluster.average_pend_time_timedelta()
    datetime.timedelta(0, 12001, 831000)
    >>> cluster.average_pend_time()
    12001.831

    .. py:attribute:: name

    This is the name of the cluster, generally this is whatever the scheduler thinks its name is, however it can be
    overridden manually by the cluster administator.

    """
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='The name of the cluster',
    )

    def get_absolute_url(self):
        """
        The absolute URL to the cluster view.

        :return: URL of the cluster view page for this instance.

        """
        args = {
        'start_time_js': 0,
        'end_time_js': 0,
        'exclude_string': "none",
        'filter_string': "cluster__id__in.%s" % self.id,
        'group_string': "none",
        }
        return reverse("lf_utilization_view", kwargs=args)

    def __unicode__(self):
        """
        Returns a unicode str containing the name of the cluster.

        :return: unicode(self.__str__())

        """
        return u'%s' % self.name

    def __str__(self):
        """
        Returns a  str containing the name of the cluster.

        :return: str(name)

        """
        return self.name

    def total_jobs(self):
        """
        Returns an total number of jobs that have been submitted to this cluster since time began.

        :return: Integer containing total number of jobs

        """
        return Job.objects.filter(attempt__cluster=self).distinct().count()

    def total_tasks(self):
        """
        Returns an total number of tasks that have been submitted to this cluster since time began.

        :return: Integer containing total number of tasks

        """
        return Task.objects.filter(attempt__cluster=self).distinct().count()

    def total_attempts(self):
        """
        Returns an total number of tasks that have been executed on this cluster since time began.

        :return: Integer containing total number of tasks

        """
        return self.attempt_set.count()

    def first_task(self):
        """
        Gets the first task that was executed on the cluster.  If no tasks were executed on the cluster, returns None.

        :return: Attempt object of the first attempt executed.

        """
        try:
            return self.attempt_set.order_by('start_time')[0]
        except:
            return None

    def last_task(self):
        """
        Gets the last task that ended on the cluster, regardless of exit status.  If no tasks have been executed on the
        cluster, returns None

        :return: Attempt object of the last attempt ended, returns None of no attempts.

        """
        try:
            return self.attempt_set.order_by('-end_time')[0]
        except:
            return None

    def last_failed_task(self):
        """
        Gets the last task that exited with a non-successful exit state on the cluster.  If no tasks have been executed
        on the cluster, or none of the tasks have exited witha  failure, returns None

        :return: Attempt object of the last attempt that failed, returns None of no failed attempts.

        """
        try:
            return self.attempt_set.exclude(status__exited_cleanly=True).order_by('-end_time')[0]
        except:
            return None

    def average_pend_time(self):
        """
        Calculates the average pend time in seconds for all jobs that executed on the cluster.

        :return: Number of seconds on average that jobs pend for on this cluster.

        """

        name = "%s_cluster_average_pend_time" % self.id
        pend = cache.get(name)
        if not pend:
            pend = self.attempt_set.aggregate(Avg('pend_time'))['pend_time__avg']
            cache.set(name, pend, 60 * 60 * 2)
        return pend

    def average_pend_time_timedelta(self):
        """
        Timedelta object of the number of seconds that jobs pend for

        :return: Average pend time as timedelta.

        """
        return datetime.timedelta(seconds=self.average_pend_time())

    def average_pend_time_percent(self):
        """
        Gets the average pend time of jobs on the cluster as a percent of their overall wall clock time.

        :return: Average Pend Time as a percent

        """
        return (float(self.average_pend_time()) / float(self.average_wall_time())) * 100

    def average_wall_time(self):
        """
        Calculates the average wall clock time in seconds for all jobs that executed on the cluster.

        :return: Number of seconds on average that jobs take from submission to completion.

        """
        name = "%s_cluster_average_wall_time" % self.id
        wall = cache.get(name)
        if not wall:
            wall = self.attempt_set.aggregate(Avg('wall_time'))['wall_time__avg']
            cache.set(name, wall, 60 * 60 * 2)
        return wall

    def average_wall_time_timedelta(self):
        """
        Timedelta object of the number of seconds of the average wall clock time.

        :return: Average wall clock time as timedelta.

        """
        return datetime.timedelta(seconds=self.average_wall_time())


class ClusterLog(models.Model):
    """
    ClusterLog objects are log entries that relate to the cluster as a whole. These can be created by tools, or through
    the admin interface by an administator.

    .. py:attribute:: cluster

    Foreign key to the Cluster that the log is part of

    .. py:attribute:: time

    Time of the log entry, in seconds since Epoch

    .. py:attribute:: message

    The message, a text field that can contain freeform text.

    """
    cluster = models.ForeignKey(Cluster)
    time = models.IntegerField()
    message = models.TextField()


class Project(models.Model):
    """
    Projects are used to store the project name that jobs were submitted to, jobs of course can be submitted to
    multiple projects, and this is also supported.  Projects are unique globally.

    .. py:attribute:: name

    This is the name of the project, as reported by the scheduler.

    """
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def get_absolute_url(self):
        """
        The absolute URL to the project view.

        :return: URL of the project view page for this instance.

        """
        args = {
        'start_time_js': 0,
        'end_time_js': 0,
        'exclude_string': "none",
        'filter_string': "project__id__in.%s" % self.id,
        'group_string': "none",
        }

    def __unicode__(self):
        """
        Returns a unicode str containing the name of the project.

        :return: unicode(self.__str__())

        """
        return u'%s' % self.name

    def __str__(self):
        """
        Returns a  str containing the name of the project.

        :return: str(name)

        """
        return self.name

    def total_jobs(self):
        """
        Returns an total number of jobs that have been submitted to this project since time began.

        :return: Integer containing total number of jobs

        """
        return Job.objects.filter(attempt__projects=self).distinct().count()

    def total_tasks(self):
        """
        Returns an total number of tasks that have been submitted to this project since time began.

        :return: Integer containing total number of tasks

        """
        return Task.objects.filter(attempt__projects=self).distinct().count()

    def total_attempts(self):
        """
        Returns an total number of tasks that have been executed under this project since time began.

        :return: Integer containing total number of tasks

        """
        return self.attempt_set.distinct().count()

    def first_task(self):
        """
        Gets the first task that was executed under this project.  If no tasks were executed, returns None.

        :return: Attempt object of the first attempt executed.

        """
        try:
            return self.attempt_set.order_by('start_time')[0]
        except:
            return None

    def last_task(self):
        """
        Gets the last task under this project that ended, regardless of exit status.  If no tasks have been executed
        on the under this project, returns None

        :return: Attempt object of the last attempt ended, returns None of no attempts.

        """
        try:
            return self.attempt_set.order_by('-end_time')[0]
        except:
            return None

    def last_failed_task(self):
        """
        Gets the last task that exited with a non-successful exit state under this project.  If no tasks have been
        executed under this project, or none of the tasks have exited with a failure, returns None.

        :return: Attempt object of the last attempt that failed, returns None of no failed attempts.

        """
        try:
            return self.attempt_set.exclude(status__exited_cleanly=True).order_by('-end_time')[0]
        except:
            return None

    def average_pend_time(self):
        """
        Calculates the average pend time in seconds for all jobs that were submitted under this project.

        :return: Number of seconds on average that jobs pend for this project.

        """
        name = "%s_project_average_pend_time" % self.id
        pend = cache.get(name)
        if not pend:
            pend = self.attempt_set.aggregate(Avg('pend_time'))['pend_time__avg']
            cache.set(name, pend, 60 * 60 * 2)
        return pend

    def average_pend_time_timedelta(self):
        """
        Timedelta object of the number of seconds that jobs pend for

        :return: Average pend time as timedelta.

        """
        return datetime.timedelta(seconds=self.average_pend_time())

    def average_pend_time_percent(self):
        """
        Gets the average pend time of jobs submitted under this project as a percent of their overall wall clock time.

        :return: Average Pend Time as a percent

        """
        return (float(self.average_pend_time()) / float(self.average_wall_time())) * 100

    def average_wall_time(self):
        """
        Calculates the average wall clock time in seconds for all jobs that were submitted under this project.

        :return: Number of seconds on average that jobs take from submission to completion.

        """
        name = "%s_project_average_wall_time" % self.id
        wall = cache.get(name)
        if not wall:
            wall = self.attempt_set.aggregate(Avg('wall_time'))['wall_time__avg']
            cache.set(name, wall, 60 * 60 * 2)
        return wall

    def average_wall_time_timedelta(self):
        """
        Timedelta object of the number of seconds of the average wall clock time.

        :return: Average wall clock time as timedelta.

        """
        return datetime.timedelta(seconds=self.average_wall_time())


class Host(models.Model):
    """
    Hosts represent actual hosts, these may be any arbitrary host, but generally are hosts that are either execution
    hosts or submission hosts.

    .. py:attribute:: name

    This is the name of the host. It is generally not the fully qualified domain name, but simply the local hostname.

    """
    name = models.CharField(max_length=100, db_index=True, unique=True)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return self.name

    def total_submitted_jobs(self):
        return Job.objects.filter(submit_host=self).count()

    def total_tasks(self):
        return self.attempt_set.distinct().count()

    def total_successful_tasks(self):
        return self.attempt_set.filter(status__exited_cleanly=True).distinct().count()

    def total_failed_tasks(self):
        return self.attempt_set.exclude(status__exited_cleanly=True).distinct().count()

    def failure_rate(self):
        try:
            return (float(self.total_failed_tasks()) / float(self.total_tasks()) * 100)
        except ZeroDivisionError:
            return 0.0

    def first_task(self):
        try:
            return self.attempt_set.order_by('start_time')[0]
        except:
            return None

    def last_task(self):
        try:
            return self.attempt_set.order_by('-end_time')[0]
        except:
            return None

    def get_absolute_url(self):
        args = {
        'start_time_js': 0,
        'end_time_js': 0,
        'exclude_string': "none",
        'filter_string': "execution_hosts__id__in.%s" % self.id,
        'group_string': "none",
        }
        return reverse("lf_utilization_view", kwargs=args)


class HostLog(ClusterLog):
    host = models.ForeignKey(Host)


class Queue(models.Model):
    cluster = models.ForeignKey(Cluster, db_index=True)
    name = models.CharField(max_length=128)

    def get_absolute_url(self):
        args = {
        'start_time_js': 0,
        'end_time_js': 0,
        'exclude_string': "none",
        'filter_string': "queue__id__in.%s" % self.id,
        'group_string': "none",
        }

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return self.name

    def total_jobs(self):
        return Job.objects.filter(attempt__queue=self).distinct().count()

    def total_tasks(self):
        return Task.objects.filter(attempt__queue=self).distinct().count()

    def total_attempts(self):
        return self.attempt_set.count()

    def first_task(self):
        try:
            return self.attempt_set.order_by('start_time')[0]
        except:
            return None

    def last_task(self):
        try:
            return self.attempt_set.order_by('-end_time')[0]
        except:
            return None

    def last_failed_task(self):
        try:
            return self.attempt_set.exclude(status__exited_cleanly=True).order_by('-end_time')[0]
        except:
            return None

    def average_pend_time(self):
        name = "%s_queue_average_pend_time" % self.id
        pend = cache.get(name)
        if not pend:
            pend = self.attempt_set.aggregate(Avg('pend_time'))['pend_time__avg']
            cache.set(name, pend, 60 * 60 * 2)
        return pend

    def average_pend_time_timedelta(self):
        return datetime.timedelta(seconds=self.average_pend_time())

    def average_pend_time_percent(self):
        return (float(self.average_pend_time()) / float(self.average_wall_time())) * 100

    def average_wall_time(self):
        name = "%s_queue_average_wall_time" % self.id
        wall = cache.get(name)
        if not wall:
            wall = self.attempt_set.aggregate(Avg('wall_time'))['wall_time__avg']
            cache.set(name, wall, 60 * 60 * 2)
        return wall

    def average_wall_time_timedelta(self):
        return datetime.timedelta(seconds=self.average_wall_time())


    class Meta:
        unique_together = ('cluster', 'name')
        index_together = [
            ('cluster', 'name'),
        ]


class QueueLog(ClusterLog):
    queue = models.ForeignKey(Queue)


class User(models.Model):
    name = models.CharField(max_length=128, db_index=True, unique=True)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return '%s' % self.name

    def total_jobs(self):
        return self.job_set.count()

    def total_tasks(self):
        return self.task_set.count()

    def total_attempts(self):
        return self.attempt_set.count()

    def first_task(self):
        try:
            return self.attempt_set.order_by('start_time')[0]
        except:
            return None

    def last_task(self):
        try:
            return self.attempt_set.order_by('-end_time')[0]
        except:
            return None

    def last_failed_task(self):
        try:
            return self.attempt_set.exclude(status__exited_cleanly=True).order_by('-end_time')[0]
        except:
            return None

    def average_pend_time(self):
        name = "%s_user_average_pend_time" % self.id
        pend = cache.get(name)
        if not pend:
            pend = self.attempt_set.aggregate(Avg('pend_time'))['pend_time__avg']
            cache.set(name, pend, 60 * 60 * 2)
        return pend

    def average_pend_time_timedelta(self):
        return datetime.timedelta(seconds=self.average_pend_time())

    def average_pend_time_percent(self):
        return (float(self.average_pend_time()) / float(self.average_wall_time())) * 100

    def average_wall_time(self):
        name = "%s_user_average_wall_time" % self.id
        wall = cache.get(name)
        if not wall:
            wall = self.attempt_set.aggregate(Avg('wall_time'))['wall_time__avg']
            cache.set(name, wall, 60 * 60 * 2)
        return wall

    def average_wall_time_timedelta(self):
        return datetime.timedelta(seconds=self.average_wall_time())

    def get_absolute_url(self):
        args = {
        'start_time_js': 0,
        'end_time_js': 0,
        'exclude_string': "none",
        'filter_string': "user__id__in.%s" % self.id,
        'group_string': "none",
        }
        return reverse("lf_utilization_view", kwargs=args)


class UserLog(ClusterLog):
    user = models.ForeignKey(User)


class Job(models.Model):
    cluster = models.ForeignKey(Cluster)
    job_id = models.IntegerField()
    user = models.ForeignKey(User)
    submit_host = models.ForeignKey(Host)
    submit_time = models.IntegerField()

    def util_chart_url(self):
        start_time_js = (self.submit_time - 60) * 1000
        end_time_js = ( self.end_time() + 60 ) * 1000
        filter_string = "job.%s" % self.id
        return reverse("lf_util_chart_view", kwargs={'start_time_js': start_time_js, 'end_time_js': end_time_js,
                                                     'filter_string': filter_string, 'exclude_string': "none",
                                                     'group_string': "none"})

    def get_absolute_url(self):
        return reverse('lf_job_detail', args=[self.id])

    def __unicode__(self):
        return u"%s" % self.job_id

    def __str__(self):
        return "%s" % self.job_id

    def submit_time_datetime(self):
        return datetime.datetime.fromtimestamp(self.submit_time)

    def submit_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.submit_time)

    def end_time(self):
        try:
            date = self.attempt_set.aggregate(Max('end_time'))['end_time__max']
            if date < 1:
                date = int(time.time())
        except:
            date = int(time.time())
        return date

    def end_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.end_time())

    def short_jobs(self):
        return self.attempt_set.filter(wall_time__lte=1)

    def exited_jobs(self):
        return self.attempt_set.exclude(status__exited_cleanly=True)

    def attempt_filter_string(self):
        return "job.%s" % self.id

    def total_pend_time(self):
        return self.attempt_set.aggregate(Sum('pend_time'))['pend_time__sum']

    def total_pend_time_timedelta(self):
        return datetime.timedelta(seconds=self.total_pend_time())

    def total_cpu_time(self):
        return self.attempt_set.aggregate(Sum('cpu_time'))['cpu_time__sum']

    def total_cpu_time_timedelta(self):
        return datetime.timedelta(seconds=self.total_cpu_time())

    def total_wall_time(self):
        return self.attempt_set.aggregate(Sum('wall_time'))['wall_time__sum']

    def total_wall_time_timedelta(self):
        return datetime.timedelta(seconds=self.total_wall_time())

    def first_task(self):
        try:
            return self.attempt_set.order_by('start_time')[0]
        except:
            return None

    def last_task(self):
        try:
            return self.attempt_set.order_by('-end_time')[0]
        except:
            return None

    class Meta:
        unique_together = ('cluster', 'job_id', 'submit_time')

        index_together = [
            ['cluster', 'user'],
            ['cluster', 'job_id', 'submit_time', ],
            ['cluster', 'user', 'submit_time'],
            ['submit_time'],
            ['cluster', 'submit_time']
        ]


class JobLog(ClusterLog):
    job = models.ForeignKey(Job)


class OpenLavaTransferFile(models.Model):
    submission_file_name = models.CharField(max_length=4096)
    execution_file_name = models.CharField(max_length=4096)
    options = models.ManyToManyField(OpenLavaTransferFileOption)


class OpenLavaResourceLimit(models.Model):
    cpu = models.IntegerField()
    file_size = models.IntegerField()
    data = models.IntegerField()
    stack = models.IntegerField()
    core = models.IntegerField()
    rss = models.IntegerField()
    run = models.IntegerField()
    process = models.IntegerField()
    swap = models.IntegerField()
    nofile = models.IntegerField()
    open_files = models.IntegerField()


class JobSubmitOpenLava(models.Model):
    job = models.OneToOneField(Job)
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=128)
    options = models.ManyToManyField(OpenLavaSubmitOption)
    num_processors = models.IntegerField()
    begin_time = models.IntegerField()

    def begin_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.begin_time)

    termination_time = models.IntegerField()

    def termination_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.termination_time)

    signal_value = models.IntegerField()
    checkpoint_period = models.IntegerField()

    def checkpoint_period_timedelta(self):
        return datetime.timedelta(minutes=self.checkpoint_period)

    restart_pid = models.IntegerField()
    resource_limits = models.OneToOneField(OpenLavaResourceLimit)
    host_specification = models.CharField(max_length=64)
    host_factor = models.FloatField()
    umask = models.IntegerField()
    queue = models.ForeignKey(Queue)
    resource_request = models.TextField()
    submit_host = models.ForeignKey(Host, related_name="submitted_openlava_jobs")
    cwd = models.CharField(max_length=256)
    checkpoint_dir = models.CharField(max_length=256)
    input_file = models.CharField(max_length=256)
    output_file = models.CharField(max_length=256)
    error_file = models.CharField(max_length=256)
    input_file_spool = models.CharField(max_length=256)
    command_spool = models.CharField(max_length=256)
    job_spool_dir = models.CharField(max_length=4096)
    submit_home_dir = models.CharField(max_length=265)
    job_file = models.CharField(max_length=265)
    asked_hosts = models.ManyToManyField(Host, related_name="requested_by_openlava_jobs")
    dependency_condition = models.CharField(max_length=4096)
    job_name = models.CharField(max_length=512)
    command = models.CharField(max_length=512)
    num_transfer_files = models.IntegerField()
    transfer_files = models.ManyToManyField(OpenLavaTransferFile)
    pre_execution_command = models.TextField()
    email_user = models.CharField(max_length=512)
    project = models.ForeignKey(Project)
    nios_port = models.IntegerField()
    max_num_processors = models.IntegerField()
    schedule_host_type = models.CharField(max_length=1024)
    login_shell = models.CharField(max_length=1024)
    user_priority = models.IntegerField()


class Task(models.Model):
    cluster = models.ForeignKey(Cluster)
    job = models.ForeignKey(Job)
    user = models.ForeignKey(User)
    task_id = models.IntegerField()

    def get_absolute_url(self):
        return reverse('lf_task_detail', args=[self.id])

    def __unicode__(self):
        return u"%s" % self.task_id

    def __str__(self):
        return "%s" % self.task_id

    def short_jobs(self):
        return self.attempt_set.filter(wall_time__lte=1)

    def exited_jobs(self):
        return self.attempt_set.exclude(status__exited_cleanly=True)

    class Meta:
        index_together = [
            ['cluster', 'job'],
            ['cluster', 'user'],
            ['user'],
            ['task_id'],
        ]


class TaskLog(JobLog):
    task = models.ForeignKey(Task)


class Attempt(models.Model):
    """

    Each time a task is started on one or more compute nodes, it is called an attempt.  Tasks that fail and are
    restarted may have multiple attempts.

    .. py:attribute:: cluster

    Cluster object that this attempt is part of.

    .. py:attribute:: job

    Job object that this attempt is part of.

    .. py:attribute:: task

    Task object that this attempt is part of.

    .. py:attribute:: user

    User object that this attempt belongs to

    .. py:attribute:: num_processors

    Number of processors this attempt was dispatched to

    .. py:attribute:: projects

    QuerySet containing all Project objects that this attempt is part of.  May be part of multiple projects
    where supported by the scheduling environment.

    .. py:attribute:: execution_hosts

    QuerySet containing all Host objects that where assigned to this attempt.  Not all scheduling systems are able to
    report which hosts were used for a task.  In that case only the primary host will be given.

    .. py:attribute:: submit_time

    The time in seconds since epoch UTC that the task was submitted to the cluster

    .. py:attribute:: start_time

    The time in seconds since epoch UTC that the task was executed

    .. py:attribute:: end_time

    The time in seconds since epoch UTC that the task ended

    .. py:attribute:: cpu_time

    The cpu time in seconds for the job.

    .. py:attribute:: wall_time

    The wall clock time in seconds for the job.

    .. py:attribute:: pend_time

    The number of seconds the job was pending

    .. py:attribute:: queue

    The Queue object the job was in

    .. py:attribute:: status

    The Exit Status of the job

    .. py:attribute:: command

    The command executed by the job

    """
    cluster = models.ForeignKey(Cluster)
    job = models.ForeignKey(Job)
    task = models.ForeignKey(Task)
    user = models.ForeignKey(User)
    num_processors = models.IntegerField()
    projects = models.ManyToManyField(Project)
    execution_hosts = models.ManyToManyField(Host)
    submit_time = models.IntegerField()

    def save(self, *args, **kwargs):
        self.submit_time = self.job.submit_time
        super(Attempt, self).save(*args, **kwargs)

    def submit_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.submit_time)

    start_time = models.IntegerField()

    def start_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.start_time)

    end_time = models.IntegerField()

    def end_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.end_time)

    cpu_time = models.IntegerField()

    def cpu_time_timedelta(self):
        return datetime.timedelta(seconds=self.cpu_time)

    wall_time = models.IntegerField()

    def wall_time_timedelta(self):
        return datetime.timedelta(seconds=self.wall_time)

    pend_time = models.IntegerField()

    def pend_time_timedelta(self):
        return datetime.timedelta(seconds=self.pend_time)

    queue = models.ForeignKey(Queue)
    status = models.ForeignKey(JobStatus)
    command = models.TextField()

    def get_absolute_url(self):
        return reverse('lf_attempt_detail', args=[self.id])

    def get_attempt_id(self):
        counter = 1
        for attempt in self.task.attempt_set.all().order_by('start_time'):
            if attempt.id == self.id:
                return counter
            counter += 1

    def get_execution_host_count(self):
        hosts = []
        for h in self.execution_hosts.all().values('pk').annotate(Count('name')):
            host = Host.objects.get(pk=h['pk'])
            hosts.append({'host': host, 'count': h['name__count']})
        return hosts

    def get_contending_jobs(self):
        return Attempt.objects.filter(end_time__gte=self.start_time, start_time__lte=self.end_time,
                                      execution_hosts__in=self.execution_hosts)

    def cluster_avg_pend_time(self):
        return Attempt.filter(num_processors=self.num_processors, cluster=self.cluster).aggregate(Avg('pend_time'))[
            'pend_time__avg']

    def cluster_avg_pend_time_timedelta(self):
        return datetime.timedelta(self.cluster_avg_pend_time)

    def queue_avg_pend_time(self):
        return Attempt.filter(num_processors=self.num_processors, queue=self.queue, cluster=self.cluster).aggregate(
            Avg('pend_time'))['pend_time__avg']

    def queue_avg_pend_time_timedelta(self):
        return datetime.timedelta(self.cluster_avg_pend_time)

    def project_avg_pend_time(self):
        return Attempt.filter(num_processors=self.num_processors, project__in=self.projects.all(),
                              cluster=self.cluster).aggregate(Avg('pend_time'))['pend_time__avg']

    def project_avg_pend_time_timedelta(self):
        return datetime.timedelta(self.cluster_avg_pend_time)


    class Meta:
        unique_together = ('cluster', 'job', 'task', 'start_time')
        index_together = [
            ['start_time', 'submit_time'],
            ['start_time','end_time',],
            ['cluster', 'job', 'task'],
            ['cluster', 'job', 'task', 'start_time', ],
            ['job', 'end_time']
        ]


class GridEngineAttemptInfo(models.Model):
    attempt = models.OneToOneField(Attempt)
    project = models.ForeignKey(Project, null=True, related_name="gridengine_projects")
    department = models.ForeignKey(Project, null=True, related_name="gridengine_departments")
    cpu_time = models.FloatField()
    integral_mem_usage = models.FloatField()
    io_usage = models.FloatField()
    catagory = models.CharField(max_length=1024)
    io_wait = models.FloatField()
    pe_task_id = models.IntegerField(null=True)
    max_vmem = models.FloatField()
    advanced_reservation_id = models.IntegerField()
    advanced_reservation_submit_time = models.IntegerField()

    def advanced_reservation_submit_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.advanced_reservation_submit_time)


class AttemptResourceUsage(models.Model):
    """
    Resource usage measures for the attempt, taken from the getrusage() system call.  Not all schedulers support
    this operation, and where not supported, this will not be created.

    .. py:attribute:: attempt

    The attempt object that this instance refers to.

    .. py:attribute:: user_time

    This is the total amount of time spent executing in user mode, in seconds.

    .. py:attribute:: system_time

    This is the total amount of time spent executing in kernel mode, in seconds.

    .. py:attribute:: max_rss

    This is the maximum resident set size used (in kilobytes).

    .. py:attribute:: integral_shared_text

    Integral shared text size.

    .. py:attribute:: integral_shared_memory

    Integral shared memory size.

    .. py:attribute:: integral_unshared_data

    Integral unshared data.

    .. py:attribute:: integral_unshared_stack

    Integral unshared stack.

    .. py:attribute:: page_reclaims

    The number of page faults serviced without any I/O activity; Here I/O activity is avoided by "reclaiming" a page
    frame from the list of pages awaiting reallocation.

    .. py:attribute:: page_faults

    The number of page faults serviced that required I/O activity.

    .. py:attribute:: swaps

    Swap Operations.

    .. py:attribute:: input_block_ops

    The number of times the filesystem had to perform input.

    .. py:attribute:: output_block_ops

    The number of times the filesystem had to perform output.

    .. py:attribute:: character_io_ops

    # of characters read/written.

    .. py:attribute:: messages_sent

    Messages sent.

    .. py:attribute:: messages_received

    Messages received.

    .. py:attribute:: num_signals

    Signals received.

    .. py:attribute:: voluntary_context_switches

    The number of times a context switch resulted due to a process voluntarily giving up the processor before its
    time slice was completed (usually to await availability of a resource).

    .. py:attribute:: involuntary_context_switches

    The number of times a context switch resulted due to a higher priority process becoming runnable or because
    the current process exceeded its time slice.

    .. py:attribute:: exact_user_time

    Exact user time used.

    """
    attempt = models.OneToOneField(Attempt, db_index=True)
    user_time = models.FloatField()
    system_time = models.FloatField()
    max_rss = models.FloatField()
    integral_shared_text = models.FloatField()
    integral_shared_memory = models.FloatField()
    integral_unshared_data = models.FloatField()
    integral_unshared_stack = models.FloatField()
    page_reclaims = models.FloatField()
    page_faults = models.FloatField()
    swaps = models.FloatField()
    input_block_ops = models.FloatField()
    output_block_ops = models.FloatField()
    character_io_ops = models.FloatField()
    messages_sent = models.FloatField()
    messages_received = models.FloatField()
    num_signals = models.FloatField()
    voluntary_context_switches = models.FloatField()
    involuntary_context_switches = models.FloatField()
    exact_user_time = models.FloatField()


class OpenLavaExitInfo(models.Model):
    attempt = models.OneToOneField(Attempt)
    user_id = models.IntegerField(db_column="user_numeric_id")
    user = models.ForeignKey(User)
    options = models.ManyToManyField(OpenLavaSubmitOption)
    begin_time = models.IntegerField()

    def begin_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.begin_time)

    termination_time = models.IntegerField()

    def termination_time_datetime(self):
        return datetime.datetime.utcfromtimestamp(self.termination_time)

    resource_request = models.TextField()
    cwd = models.CharField(max_length=256)
    input_file = models.CharField(max_length=256)
    output_file = models.CharField(max_length=256)
    error_file = models.CharField(max_length=256)
    input_file_spool = models.CharField(max_length=256)
    command_spool = models.CharField(max_length=256)
    job_file = models.CharField(max_length=265)
    asked_hosts = models.ManyToManyField(Host)
    host_factor = models.FloatField()
    job_name = models.CharField(max_length=512)
    dependency_condition = models.CharField(max_length=4096)
    pre_execution_command = models.TextField()
    email_user = models.CharField(max_length=512)
    project = models.ForeignKey(Project)
    exit_status = models.IntegerField()
    max_num_processors = models.IntegerField()
    login_shell = models.CharField(max_length=1024)
    array_index = models.IntegerField()
    max_residual_mem = models.IntegerField()
    max_swap = models.IntegerField()

