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

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.middleware.csrf import get_token
from scipy.interpolate import interp1d

from lavaFlow.models import *


FILTER_FIELDS = [
    {
        'filter_string': 'status__name',
        'display_name': 'Exit Status',
        'can_select_values': True,
    },
    {
        'filter_string': 'status__exited_cleanly',
        'display_name': 'Exited OK',
        'can_select_values': True,
    },
    {
        'filter_string': 'queue__name',
        'display_name': 'Queue Name',
        'can_select_values': True,
    },
    {
        'filter_string': 'pend_time',
        'display_name': 'Pend Time',
        'can_enter_range': True,
    },
    {
        'filter_string': 'wall_time',
        'display_name': 'Wall Clock Time',
        'can_enter_range': True,
    },
    {
        'filter_string': 'cpu_time',
        'display_name': 'CPU Time',
        'can_enter_range': True,
    },
    {
        'filter_string': 'start_hour_of_day',
        'display_name': 'Start Hour',
        'can_select_values': True,
        'conversion': 'hour_of_day'
    },
    {
        'filter_string': 'start_month',
        'display_name': 'Start Month',
        'can_select_values': True,
        'conversion': 'month'
    },
    {
        'filter_string': 'start_week_of_year',
        'display_name': 'Start Week Number',
        'can_select_values': True,
        'conversion': 'week'
    },
    {
        'filter_string': 'start_day_of_week',
        'display_name': 'Start Day of Week',
        'can_select_values': True,
        'conversion': "day_of_week"
    },
    {
        'filter_string': 'start_day_of_month',
        'display_name': 'Start Day of Month',
        'can_select_values': True,
        'conversion': "day_of_month"
    },
    {
        'filter_string': 'start_time',
        'display_name': 'Start Time',
        'can_select_date': True,
        'can_enter_range': True,
    },
    {
        'filter_string': 'end_hour_of_day',
        'display_name': 'End Hour',
        'can_select_values': True,
        'conversion': "hour_of_day"
    },
    {
        'filter_string': 'end_month',
        'display_name': 'End Month',
        'can_select_values': True,
        'conversion': "month"
    },
    {
        'filter_string': 'end_week_of_year',
        'display_name': 'End Week Number',
        'can_select_values': True,
        'conversion': "week",
    },
    {
        'filter_string': 'end_day_of_week',
        'display_name': 'End Day of Week',
        'can_select_values': True,
        'conversion': "day_of_week"
    },
    {
        'filter_string': 'end_day_of_month',
        'display_name': 'End Day of Month',
        'can_select_values': True,
        'conversion': "day_of_month"
    },
    {
        'filter_string': 'end_time',
        'display_name': 'End Time',
        'can_select_date': True,
        'can_enter_range': True,
    },
    {
        'filter_string': 'submit_hour_of_day',
        'display_name': 'Submit Hour',
        'can_select_values': True,
        'conversion': "hour_of_day",
    },
    {
        'filter_string': 'submit_month',
        'display_name': 'Submit Month',
        'can_select_values': True,
        'conversion': "month"
    },
    {
        'filter_string': 'submit_week_of_year',
        'display_name': 'Submit Week Number',
        'can_select_values': True,
        'conversion': "week_of_year"
    },
    {
        'filter_string': 'submit_day_of_week',
        'display_name': 'Submit Day of Week',
        'can_select_values': True,
        'conversion': "day_of_week"
    },
    {
        'filter_string': 'submit_day_of_month',
        'display_name': 'Submit Day of Month',
        'can_select_values': True,
        'conversion': "day_of_month"
    },
    {
        'filter_string': 'submit_time',
        'display_name': 'Submit Time',
        'can_select_date': True,
        'can_enter_range': True,

    },
    {
        'filter_string': 'execution_hosts__name',
        'display_name': 'Execution Host',
        'can_select_values': True,
    },
    {
        'filter_string': 'projects__name',
        'display_name': 'Project',
        'can_select_values': True,
    },
    {
        'filter_string': 'user__name',
        'display_name': 'Owner',
        'can_select_values': True,
    },
    {
        'filter_string': 'task__task_id',
        'display_name': 'Task ID',
        'can_enter_range': True,
    },
    {
        'filter_string': 'job__job_id',
        'display_name': 'Job ID',
        'can_enter_range': True,
    },
    {
        'filter_string': 'cluster__name',
        'display_name': 'Cluster',
        'can_select_values': True,
    },
    {
        'filter_string': 'cluster__id',
        'display_name': 'Cluster ID',
        'can_select_values': True,
    },
    {
        'filter_string': 'queue__id',
        'display_name': 'Queue ID',
        'can_select_values': True,
    },
    {
        'filter_string': 'projects__id',
        'display_name': 'Project ID',
        'can_select_values': True,
    },
    {
        'filter_string': 'execution_hosts__id',
        'display_name': 'Execution Host ID',
        'can_select_values': True,
    },
    {
        'filter_string': 'user__id',
        'display_name': 'User FK ID',
        'can_select_values': True,
    },
]


def get_friendly_val(field, value):
    hour_of_day = {
        0: "00:00",
        1: "01:00",
        2: "02:00",
        3: "03:00",
        4: "04:00",
        5: "05:00",
        6: "06:00",
        7: "07:00",
        8: "08:00",
        9: "09:00",
        10: "10:00",
        11: "11:00",
        12: "12:00",
        13: "13:00",
        14: "14:00",
        15: "15:00",
        16: "16:00",
        17: "17:00",
        18: "18:00",
        19: "19:00",
        20: "20:00",
        21: "21:00",
        22: "22:00",
        23: "23:00",
    }
    months = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }
    days = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }
    lookups = {
        'hour_of_day': lambda n: hour_of_day[n],
        'month': lambda n: months[n],
        'week': lambda n: "Week %s" % n,
        'day_of_week': lambda n: days[n],
        'day_of_month': format_month_day,
    }
    f = lookups[field]
    return f(value)


def format_month_day(day):
    if str(day).endswith("1"):
        return "%sst" % day
    if str(day).endswith("2"):
        return "%snd" % day
    if str(day).endswith("3"):
        return "%srd" % day
    return "%sth" % day


OPENLAVA_JOB_STATES = {
    0x00: {
        'friendly': "Null",
        'name': 'JOB_STAT_NULL',
        'description': 'State null.',
    },
    0x01: {
        'friendly': "Pending",
        'name': 'JOB_STAT_PEND',
        'description': 'The job is pending, i.e., it has not been dispatched yet.',
    },
    0x02: {
        'friendly': "Held",
        'name': "JOB_STAT_PSUSP",
        'description': "The pending job was suspended by its owner or the LSF system administrator.",
    },
    0x04: {
        'friendly': "Running",
        'name': "JOB_STAT_RUN",
        'description': "The job is running.",
    },
    0x08: {
        'friendly': "Suspended by system",
        'name': "JOB_STAT_SSUSP",
        'description': "The running job was suspended by the system because an execution host was overloaded or the \
        queue run window closed.",
    },
    0x10: {
        'friendly': "Suspended by user",
        'name': "JOB_STAT_USUSP",
        'description': "The running job was suspended by its owner or the LSF system administrator.",
    },
    0x20: {
        'friendly': "Exited",
        'name': "JOB_STAT_EXIT",
        'description': "The job has terminated with a non-zero status - it may have been aborted due to an error in \
        its execution, or killed by its owner or by the LSF system administrator.",
    },
    0x40: {
        'friendly': "Completed",
        'name': "JOB_STAT_DONE",
        'description': "The job has terminated with status 0.",
    },
    0x80: {
        'friendly': "Process Completed",
        'name': "JOB_STAT_PDONE",
        'description': "Post job process done successfully.",
    },
    0x100: {
        'friendly': "Process Error",
        'name': "JOB_STAT_PERR",
        'description': "Post job process has error.",
    },
    0x200: {
        'friendly': "Waiting for execution",
        'name': "JOB_STAT_WAIT",
        'description': "Chunk job waiting its turn to exec.",
    },
    0x10000: {
        'friendly': "Unknown",
        'name': "JOB_STAT_UNKWN",
        'description': "The subordinate batch daemon (sbatchd) on the host on which the job is processed has lost contact \
        with the main batch daemon (mbatchd).",
    },
}


@ensure_csrf_cookie
def get_csrf_token(request):
    """Returns the CSRF token to the client as part of a json document.

    :param request: Request object
    :return: HttpResponse with cookie containing JSON data.

    """
    return create_js_success(data={'cookie': get_token(request)}, message="")


def create_js_success(data=None, message=""):
    """Takes a json serializable object, and an optional message, and creates a standard json response document.

    :param data: json serializable object
    :param message: Optional message to include with response
    :return: HttpResponse object

    """
    data = {
        'status': "OK",
        'data': data,
        'message': message,
    }
    return HttpResponse(json.dumps(data, indent=3, sort_keys=True), content_type="application/json")


def create_js_bad_request(data=None, message=""):
    """Takes an optional json serializable object, and an optional message, and creates a standard json
     response using a HttpResponseBadRequest class.

    :param data: json serializable object
    :param message: Optional message to include with response
    :return: HttpResponse object

    """
    data = {
        'status': "OK",
        'data': data,
        'message': message,
    }
    return HttpResponseBadRequest(json.dumps(data, indent=3, sort_keys=True), content_type="application/json")


@csrf_exempt
def gridengine_import(request, cluster_name):
    # Parse the body for json data
    try:
        data = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON data")

    # check it contains the upload key
    if 'key' not in data:
        return HttpResponseBadRequest("key not specified")

    # Check the key is valid
    try:
        ImportKey.objects.get(client_key=data['key'])
    except ObjectDoesNotExist:
        print "failed Key"
        return HttpResponseForbidden("Invalid key specified")

    # Get or create the cluster
    (cluster, created) = Cluster.objects.get_or_create(name=cluster_name)

    # Process each entry in the array of entries
    for event in data['payload']:
        gridengine_job_import(cluster, event)

    return create_js_success(message="Import Successful")


def gridengine_job_import(cluster, data):
    (user, created) = User.objects.get_or_create(name=data['owner'])
    (submit_host, created) = Host.objects.get_or_create(name="Unspecified")
    (job, created) = Job.objects.get_or_create(cluster=cluster, job_id=data['job_number'], user=user,
                                               submit_host=submit_host, submit_time=data['submission_time'])
    (queue, created) = Queue.objects.get_or_create(name=data['qname'], cluster=cluster)
    (task, created) = Task.objects.get_or_create(cluster=cluster, job=job, user=user, task_id=data['task_number'])
    num_processors = data['slots']
    start_time = data['start_time']
    end_time = data['end_time']
    wall_time = end_time - start_time
    cpu_time = num_processors * wall_time
    submit_time = data['submission_time']
    pend_time = start_time - submit_time

    states = {
        0: {
            'code': 0,
            'name': "No Failure",
            'description': "Ran and Exited normally",
            'exited_cleanly': True,
        },
        1: {
            'code': 1,
            'name': "Assumedly before job",
            'description': 'failed early in execd',
            'exited_cleanly': False,
        },
        3: {
            'code': 3,
            'name': 'Before writing config',
            'description': 'failed before execd set up local spool',
            'exited_cleanly': False,
        },
        4: {
            'code': 4,
            'name': 'Before writing PID',
            'description': 'shepherd failed to record its pid',
            'exited_cleanly': False,
        },
        6: {
            'code': 6,
            'name': 'Setting processor set',
            'description': 'failed setting up processor set',
            'exited_cleanly': False,
        },
        7: {
            'code': 7,
            'name': 'Before prolog',
            'description': 'failed before prolog',
            'exited_cleanly': False,
        },
        8: {
            'code': 8,
            'name': 'In prolog',
            'description': 'failed in prolog',
            'exited_cleanly': False,
        },
        9: {
            'code': 9,
            'name': 'Before pestart',
            'description': 'failed before starting PE',
            'exited_cleanly': False,
        },
        10: {
            'code': 10,
            'name': 'in pestart',
            'description': 'failed in PE starter',
            'exited_cleanly': False,
        },
        11: {
            'code': 11,
            'name': 'Before job',
            'description': 'failed in shepherd before starting job',
            'exited_cleanly': False,
        },
        12: {
            'code': 12,
            'name': 'Before PE Stop',
            'description': 'ran, but failed before calling PE stop procedure',
            'exited_cleanly': True,
        },
        13: {
            'code': 13,
            'name': 'In PE Stop',
            'description': 'ran, but PE stop procedure failed',
            'exited_cleanly': True,
        },
        14: {
            'code': 14,
            'name': 'Before Epilog',
            'description': 'ran, but failed in epilog script',
            'exited_cleanly': True,
        },
        16: {
            'code': 16,
            'name': 'Releasing processor set',
            'description': 'ran, but processor set could not be released',
            'exited_cleanly': True,
        },
        17: {
            'code': 17,
            'name': 'Through signal',
            'description': 'job killed by signal (possibly qdel)',
            'exited_cleanly': True,
        },
        18: {
            'code': 18,
            'name': 'Shepherd returned error',
            'description': 'Shephard Died',
            'exited_cleanly': False,
        },
        19: {
            'code': 19,
            'name': 'Before writing exit_status',
            'description': 'shepherd didnt write reports corectly',
            'exited_cleanly': False,
        },
        20: {
            'code': 20,
            'name': 'Found unexpected error file',
            'description': 'shepherd encountered a problem',
            'exited_cleanly': True,
        },
        21: {
            'code': 21,
            'name': 'In recognizing job',
            'description': 'qmain asked about an unknown job (Not in accounting)',
            'exited_cleanly': False,
        },
        24: {
            'code': 24,
            'name': 'Migrating (checkpointing jobs)',
            'description': 'ran, will be migrated',
            'exited_cleanly': True,
        },
        25: {
            'code': 25,
            'name': 'Rescheduling',
            'description': 'ran, will be rescheduled',
            'exited_cleanly': True,
        },
        26: {
            'code': 26,
            'name': 'Opening output file',
            'description': 'failed opening stderr/stdout file',
            'exited_cleanly': False,
        },
        27: {
            'code': 27,
            'name': 'Searching requested shell',
            'description': 'failed finding specified shell',
            'exited_cleanly': False,
        },
        28: {
            'code': 28,
            'name': 'Changing to working directory',
            'description': 'failed changing to start directory',
            'exited_cleanly': False,
        },
        29: {
            'code': 29,
            'name': 'AFS setup',
            'description': 'failed setting up AFS security',
            'exited_cleanly': False,
        },
        30: {
            'code': 30,
            'name': 'Application error returned',
            'description': 'ran and exited 100 - maybe re-scheduled',
            'exited_cleanly': True,
        },
        31: {
            'code': 31,
            'name': 'Accessing sgepasswd file',
            'description': 'failed because sgepasswd not readable (MS Windows)',
            'exited_cleanly': False,
        },
        32: {
            'code': 32,
            'name': 'entry is missing in password file',
            'description': 'failed because user not in sgepasswd (MS Windows)',
            'exited_cleanly': False,
        },
        33: {
            'code': 33,
            'name': 'Wrong password',
            'description': 'failed because of wrong password against sgepasswd (MS Windows)',
            'exited_cleanly': False,
        },
        34: {
            'code': 34,
            'name': 'Communicating with Grid Engine Helper Service',
            'description': 'failed because of failure of helper service (MS Windows)',
            'exited_cleanly': False,
        },
        35: {
            'code': 35,
            'name': 'Before job in Grid Engine Helper Service',
            'description': 'failed because of failure running helper service (MS Windows)',
            'exited_cleanly': False,
        },
        36: {
            'code': 36,
            'name': 'Checking configured daemons',
            'description': 'failed because of configured remote startup daemon',
            'exited_cleanly': False,
        },
        37: {
            'code': 37,
            'name': 'qmain enforced h_rt, h_cpu, or h_vmem limit',
            'description': 'ran, but killed due to exceeding run time limit',
            'exited_cleanly': True,
        },
        38: {
            'code': 38,
            'name': 'Adding supplementary group',
            'description': 'failed adding supplementary gid to job',
            'exited_cleanly': False,
        },
        100: {
            'code': 100,
            'name': 'Assumedly after job',
            'description': 'ran, but killed by a signal (perhaps due to exceeding resources), task died, shepherd \
            died (e.g. node crash), etc.',
            'exited_cleanly': True,
        },
    }
    state = states[data['failed']]
    (status, created) = JobStatus.objects.get_or_create(**state)
    (attempt, created) = Attempt.objects.get_or_create(
        cluster=cluster,
        job=job,
        task=task,
        start_time=start_time,
        defaults={
            'user': user,
            'num_processors': num_processors,
            'end_time': end_time,
            'cpu_time': cpu_time,
            'wall_time': wall_time,
            'pend_time': pend_time,
            'queue': queue,
            'status': status,
            'command': "Unspecified",
        },
    )
    if created:
        (execution_host, created) = Host.objects.get_or_create(name=data['hostname'])
        attempt.execution_hosts.add(execution_host)
        dept = None
        project = None
        if data['project']:
            (project, created) = Project.objects.get_or_create(name=data['project'])
            attempt.projects.add(project)
        if data['department']:
            (dept, created) = Project.objects.get_or_create(name=data['department'])
            attempt.projects.add(dept)
        r = AttemptResourceUsage()
        r.attempt = attempt
        r.user_time = data['ru_utime']
        r.system_time = data['ru_stime']
        r.max_rss = data['ru_maxrss']
        r.integral_shared_text = -1
        r.integral_shared_memory = data['ru_ixrss']
        r.integral_unshared_data = data['ru_idrss']
        r.integral_unshared_stack = data['ru_isrss']
        r.page_reclaims = data['ru_minflt']
        r.page_faults = data['ru_majflt']
        r.swaps = data['ru_nswap']
        r.input_block_ops = data['ru_inblock']
        r.output_block_ops = data['ru_oublock']
        r.character_io_ops = -1
        r.messages_sent = data['ru_msgsnd']
        r.messages_received = data['ru_msgrcv']
        r.num_signals = data['ru_nsignals']
        r.voluntary_context_switches = data['ru_nvcsw']
        r.involuntary_context_switches = data['ru_nivcsw']
        r.exact_user_time = -1
        r.save()
        a = GridEngineAttemptInfo()
        a.attempt = attempt
        a.project = project
        a.department = dept
        a.cpu_time = data['cpu']
        a.integral_mem_usage = data['mem']
        a.io_usage = data['io']
        a.category = ""
        if data['category']:
            a.category = data['category']
        a.io_wait = data['iow']
        a.pe_task_id = data['pe_taskid']
        a.max_vmem = data['maxvmem']
        a.advanced_reservation_id = data['arid']
        a.advanced_reservation_submit_time = data['ar_submission_time']
        a.save()


@csrf_exempt
def univa82_import(request, cluster_name):
    # Parse the body for json data
    try:
        data = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON data")

    # check it contains the upload key
    if 'key' not in data:
        return HttpResponseBadRequest("key not specified")

    # Check the key is valid
    try:
        ImportKey.objects.get(client_key=data['key'])
    except ObjectDoesNotExist:
        print "failed Key"
        return HttpResponseForbidden("Invalid key specified")

    # Get or create the cluster
    (cluster, created) = Cluster.objects.get_or_create(name=cluster_name)

    # Process each entry in the array of entries
    for event in data['payload']:
        univa82_job_import(cluster, event)

    return create_js_success(message="Import Successful")


def univa82_job_import(cluster, data):
    (user, created) = User.objects.get_or_create(name=data['owner'])
    (submit_host, created) = Host.objects.get_or_create(name=data['submit_host'])
    (job, created) = Job.objects.get_or_create(cluster=cluster, job_id=data['job_number'], user=user,
                                               submit_host=submit_host, submit_time=int(data['submission_time']))
    (queue, created) = Queue.objects.get_or_create(name=data['qname'], cluster=cluster)
    (task, created) = Task.objects.get_or_create(cluster=cluster, job=job, user=user, task_id=data['task_number'])
    num_processors = data['slots']
    start_time = int(data['start_time'])  # start_time is a float
    end_time = int(data['end_time'])
    wall_time = end_time - start_time
    cpu_time = num_processors * wall_time
    submit_time = int(data['submission_time'])  # float...
    pend_time = start_time - submit_time

    states = {
        0: {
            'code': 0,
            'name': "No Failure",
            'description': "Ran and Exited normally",
            'exited_cleanly': True,
        },
        1: {
            'code': 1,
            'name': "Assumedly before job",
            'description': 'failed early in execd',
            'exited_cleanly': False,
        },
        3: {
            'code': 3,
            'name': 'Before writing config',
            'description': 'failed before execd set up local spool',
            'exited_cleanly': False,
        },
        4: {
            'code': 4,
            'name': 'Before writing PID',
            'description': 'shepherd failed to record its pid',
            'exited_cleanly': False,
        },
        6: {
            'code': 6,
            'name': 'Setting processor set',
            'description': 'failed setting up processor set',
            'exited_cleanly': False,
        },
        7: {
            'code': 7,
            'name': 'Before prolog',
            'description': 'failed before prolog',
            'exited_cleanly': False,
        },
        8: {
            'code': 8,
            'name': 'In prolog',
            'description': 'failed in prolog',
            'exited_cleanly': False,
        },
        9: {
            'code': 9,
            'name': 'Before pestart',
            'description': 'failed before starting PE',
            'exited_cleanly': False,
        },
        10: {
            'code': 10,
            'name': 'in pestart',
            'description': 'failed in PE starter',
            'exited_cleanly': False,
        },
        11: {
            'code': 11,
            'name': 'Before job',
            'description': 'failed in shepherd before starting job',
            'exited_cleanly': False,
        },
        12: {
            'code': 12,
            'name': 'Before PE Stop',
            'description': 'ran, but failed before calling PE stop procedure',
            'exited_cleanly': True,
        },
        13: {
            'code': 13,
            'name': 'In PE Stop',
            'description': 'ran, but PE stop procedure failed',
            'exited_cleanly': True,
        },
        14: {
            'code': 14,
            'name': 'Before Epilog',
            'description': 'ran, but failed in epilog script',
            'exited_cleanly': True,
        },
        16: {
            'code': 16,
            'name': 'Releasing processor set',
            'description': 'ran, but processor set could not be released',
            'exited_cleanly': True,
        },
        17: {
            'code': 17,
            'name': 'Through signal',
            'description': 'job killed by signal (possibly qdel)',
            'exited_cleanly': True,
        },
        18: {
            'code': 18,
            'name': 'Shepherd returned error',
            'description': 'Shephard Died',
            'exited_cleanly': False,
        },
        19: {
            'code': 19,
            'name': 'Before writing exit_status',
            'description': 'shepherd didnt write reports correctly',
            'exited_cleanly': False,
        },
        20: {
            'code': 20,
            'name': 'Found unexpected error file',
            'description': 'shepherd encountered a problem',
            'exited_cleanly': True,
        },
        21: {
            'code': 21,
            'name': 'In recognizing job',
            'description': 'qmain asked about an unknown job (Not in accounting)',
            'exited_cleanly': False,
        },
        24: {
            'code': 24,
            'name': 'Migrating (checkpointing jobs)',
            'description': 'ran, will be migrated',
            'exited_cleanly': True,
        },
        25: {
            'code': 25,
            'name': 'Rescheduling',
            'description': 'ran, will be rescheduled',
            'exited_cleanly': True,
        },
        26: {
            'code': 26,
            'name': 'Opening output file',
            'description': 'failed opening stderr/stdout file',
            'exited_cleanly': False,
        },
        27: {
            'code': 27,
            'name': 'Searching requested shell',
            'description': 'failed finding specified shell',
            'exited_cleanly': False,
        },
        28: {
            'code': 28,
            'name': 'Changing to working directory',
            'description': 'failed changing to start directory',
            'exited_cleanly': False,
        },
        29: {
            'code': 29,
            'name': 'AFS setup',
            'description': 'failed setting up AFS security',
            'exited_cleanly': False,
        },
        30: {
            'code': 30,
            'name': 'Application error returned',
            'description': 'ran and exited 100 - maybe re-scheduled',
            'exited_cleanly': True,
        },
        31: {
            'code': 31,
            'name': 'Accessing sgepasswd file',
            'description': 'failed because sgepasswd not readable (MS Windows)',
            'exited_cleanly': False,
        },
        32: {
            'code': 32,
            'name': 'entry is missing in password file',
            'description': 'failed because user not in sgepasswd (MS Windows)',
            'exited_cleanly': False,
        },
        33: {
            'code': 33,
            'name': 'Wrong password',
            'description': 'failed because of wrong password against sgepasswd (MS Windows)',
            'exited_cleanly': False,
        },
        34: {
            'code': 34,
            'name': 'Communicating with Grid Engine Helper Service',
            'description': 'failed because of failure of helper service (MS Windows)',
            'exited_cleanly': False,
        },
        35: {
            'code': 35,
            'name': 'Before job in Grid Engine Helper Service',
            'description': 'failed because of failure running helper service (MS Windows)',
            'exited_cleanly': False,
        },
        36: {
            'code': 36,
            'name': 'Checking configured daemons',
            'description': 'failed because of configured remote startup daemon',
            'exited_cleanly': False,
        },
        37: {
            'code': 37,
            'name': 'qmain enforced h_rt, h_cpu, or h_vmem limit',
            'description': 'ran, but killed due to exceeding run time limit',
            'exited_cleanly': True,
        },
        38: {
            'code': 38,
            'name': 'Adding supplementary group',
            'description': 'failed adding supplementary gid to job',
            'exited_cleanly': False,
        },
        100: {
            'code': 100,
            'name': 'Assumedly after job',
            'description': 'ran, but killed by a signal (perhaps due to exceeding resources), task died, \
            shepherd died (e.g. node crash), etc.',
            'exited_cleanly': True,
        },
    }
    state = states[data['failed']]
    (status, created) = JobStatus.objects.get_or_create(**state)
    (attempt, created) = Attempt.objects.get_or_create(
        cluster=cluster,
        job=job,
        task=task,
        start_time=start_time,
        defaults={
            'user': user,
            'num_processors': num_processors,
            'end_time': end_time,
            'cpu_time': cpu_time,
            'wall_time': wall_time,
            'pend_time': pend_time,
            'queue': queue,
            'status': status,
            'command': "Unspecified",
        },
    )
    if created or end_time > attempt.end_time:
        attempt.execution_hosts.clear()
        (execution_host, created) = Host.objects.get_or_create(name=data['hostname'])
        attempt.execution_hosts.add(execution_host)
        dept = None
        project = None
        attempt.projects.clear()
        if data['project']:
            (project, created) = Project.objects.get_or_create(name=data['project'])
            attempt.projects.add(project)
        if data['department']:
            (dept, created) = Project.objects.get_or_create(name=data['department'])
            attempt.projects.add(dept)

        try:
            r = attempt.attemptresourceusage
        except ObjectDoesNotExist:
            r = AttemptResourceUsage()
            r.attempt = attempt
        r.user_time = data['ru_utime']
        r.system_time = data['ru_stime']
        r.max_rss = data['ru_maxrss']
        r.integral_shared_text = -1
        r.integral_shared_memory = data['ru_ixrss']
        r.integral_unshared_data = data['ru_idrss']
        r.integral_unshared_stack = data['ru_isrss']
        r.page_reclaims = data['ru_minflt']
        r.page_faults = data['ru_majflt']
        r.swaps = data['ru_nswap']
        r.input_block_ops = data['ru_inblock']
        r.output_block_ops = data['ru_oublock']
        r.character_io_ops = -1
        r.messages_sent = data['ru_msgsnd']
        r.messages_received = data['ru_msgrcv']
        r.num_signals = data['ru_nsignals']
        r.voluntary_context_switches = data['ru_nvcsw']
        r.involuntary_context_switches = data['ru_nivcsw']
        r.exact_user_time = -1
        r.save()

        try:
            a = attempt.gridengineattemptinfo
        except ObjectDoesNotExist:
            a = GridEngineAttemptInfo()
            a.attempt = attempt

        a.project = project
        a.department = dept
        a.cpu_time = data['cpu']
        a.integral_mem_usage = data['mem']
        a.io_usage = data['io']
        a.category = ""
        if data['category']:
            a.category = data['category']
        a.io_wait = data['iow']
        a.pe_task_id = data['pe_taskid']
        a.max_vmem = data['maxvmem']
        a.advanced_reservation_id = data['arid']
        a.advanced_reservation_submit_time = data['ar_submission_time']
        a.save()


@csrf_exempt
def openlava_import(request, cluster_name):
    """Imports one or more openlava log entries, log entries are uploaded as JSON data in the request body.

    :param request: Request object
    :param cluster_name: name of cluster (Specified in URL)
    :return: JSON Status

    """
    # Parse the body for json data
    try:
        data = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON data")

    # check it contains the upload key
    if 'key' not in data:
        return HttpResponseBadRequest("key not specified")

    # Check the key is valid
    try:
        ImportKey.objects.get(client_key=data['key'])
    except ObjectDoesNotExist:
        return HttpResponseForbidden("Invalid key specified")

    # Get or create the cluster
    (cluster, created) = Cluster.objects.get_or_create(name=cluster_name)

    # Process each entry in the array of entries
    for event in data['payload']:
        if event['type'] == 1:  # EVENT_JOB_NEW
            openlava_import_job_new(cluster, event)
        elif event['type'] == 10:  # EVENT_JOB_FINISH
            openlava_import_job_finish(cluster, event)

    return create_js_success(message="Import Successful")


def openlava_import_job_new(cluster, event):
    """Imports a single openlava job_new event event.

    :param cluster: Cluster object
    :param event: Dict containing event details
    :return: None

    """
    event = event['eventLog']['jobNewLog']

    (user, created) = User.objects.get_or_create(name=event['userName'])
    (submit_host, created) = Host.objects.get_or_create(name=event['fromHost'])
    (job, created) = Job.objects.get_or_create(
        cluster=cluster,
        job_id=event['jobId'],
        user=user,
        submit_host=submit_host,
        submit_time=event['submitTime'])
    (queue, created) = Queue.objects.get_or_create(name=event['queue'], cluster=cluster)
    try:
        job.jobsubmitopenlava
    except ObjectDoesNotExist:
        js = JobSubmitOpenLava()
        js.job = job
        (project, created) = Project.objects.get_or_create(name=event['projectName'])
        js.project = project
        js.user_name = user.name
        js.queue = queue
        js.submit_host = submit_host

        limit = OpenLavaResourceLimit()
        limit.cpu = event['rLimits'][0]
        limit.file_size = event['rLimits'][1]
        limit.data = event['rLimits'][2]
        limit.stack = event['rLimits'][3]
        limit.core = event['rLimits'][4]
        limit.rss = event['rLimits'][5]
        limit.run = event['rLimits'][9]
        limit.process = event['rLimits'][10]
        limit.swap = event['rLimits'][8]
        limit.nofile = event['rLimits'][6]
        limit.open_files = event['rLimits'][7]
        limit.save()

        js.resource_limits = limit
        js.user_id = event['userId']
        js.num_processors = event['numProcessors']
        js.begin_time = event['beginTime']
        js.termination_time = event['termTime']
        js.signal_value = event['sigValue']
        js.checkpoint_period = event['chkpntPeriod']
        js.restart_pid = event['restartPid']
        js.host_specification = event['hostSpec']
        js.host_factor = event['hostFactor']
        js.umask = event['umask']
        js.resource_request = event['resReq']
        js.cwd = event['cwd']
        js.checkpoint_dir = event['chkpntDir']
        js.input_file = event['inFile']
        js.output_file = event['outFile']
        js.error_file = event['errFile']
        js.input_file_spool = event['inFileSpool']
        js.command_spool = event['commandSpool']
        js.job_spool_dir = event['jobSpoolDir']
        js.submit_home_dir = event['subHomeDir']
        js.job_file = event['jobFile']
        js.dependency_condition = event['dependCond']
        js.job_name = event['jobName']
        js.command = event['command']
        js.num_transfer_files = event['nxf']
        js.pre_execution_cmd = event['preExecCmd']
        js.email_user = event['mailUser']
        js.nios_port = event['niosPort']
        js.max_num_processors = event['maxNumProcessors']
        js.schedule_host_type = event['schedHostType']
        js.login_shell = event['loginShell']
        js.user_priority = event['userPriority']
        js.save()
        for host in event['askedHosts']:
            (h, created) = Host.objects.get_or_create(name=host)
            js.asked_hosts.add(h)
        for fl in event['xf']:
            f = OpenLavaTransferFile()
            f.submission_file_name = fl['subFn']
            f.execution_file_name = fl['execFn']
            f.save()
            js.transfer_files.add(f)

            for state in OpenLavaSubmitOption.get_status_list(event['options']):
                (o, created) = OpenLavaSubmitOption.objects.get_or_create(**state)
                js.options.add(o)


def openlava_import_job_finish(cluster, event):
    """Imports a single openlava job finish event.

    :param cluster: Cluster object
    :param event: event to import
    :return: None

    """
    log_entry = event['eventLog']['jobFinishLog']

    (user, created) = User.objects.get_or_create(name=log_entry['userName'])
    (submit_host, created) = Host.objects.get_or_create(name=log_entry['fromHost'])
    (job, created) = Job.objects.get_or_create(
        cluster=cluster,
        job_id=log_entry['jobId'],
        user=user,
        submit_host=submit_host,
        submit_time=log_entry['submitTime'])

    (task, created) = Task.objects.get_or_create(cluster=cluster, job=job, user=user, task_id=log_entry['idx'])
    num_processors = log_entry['numProcessors']
    start_time = log_entry['startTime']
    if start_time == 0:  # Job was killed before starting
        start_time = event['eventTime']

    end_time = event['eventTime']

    wall_time = end_time - start_time
    cpu_time = wall_time * num_processors
    pend_time = event['eventTime'] - log_entry['submitTime']

    if start_time > 0:  # 0 == job didn't start
        pend_time = start_time - log_entry['submitTime']

    (queue, created) = Queue.objects.get_or_create(name=log_entry['queue'], cluster=cluster)

    job_state = OPENLAVA_JOB_STATES[log_entry['jStatus']]
    clean = False
    if job_state['name'] == "JOB_STAT_DONE":
        clean = True
    (status, created) = JobStatus.objects.get_or_create(
        code=log_entry['jStatus'],
        name=job_state['friendly'],
        description=job_state['description'],
        exited_cleanly=clean,
    )

    (attempt, created) = Attempt.objects.get_or_create(
        cluster=cluster,
        job=job,
        task=task,
        start_time=start_time,
        defaults={
            'user': user,
            'num_processors': num_processors,
            'end_time': end_time,
            'cpu_time': cpu_time,
            'wall_time': wall_time,
            'pend_time': pend_time,
            'queue': queue,
            'status': status,
            'command': log_entry['command'],
        },
    )

    if created:
        for host in log_entry['execHosts']:
            (execution_host, created) = Host.objects.get_or_create(name=host)
            attempt.execution_hosts.add(execution_host)

        (project, created) = Project.objects.get_or_create(name=log_entry['projectName'])
        attempt.projects.add(project)

        try:
            resource_usage = attempt.attemptresourceusage
        except ObjectDoesNotExist:
            resource_usage = AttemptResourceUsage()
            resource_usage.user_time = log_entry['lsfRusage']['ru_utime']
            resource_usage.system_time = log_entry['lsfRusage']['ru_stime']
            resource_usage.max_rss = log_entry['lsfRusage']['ru_maxrss']
            resource_usage.integral_shared_text = log_entry['lsfRusage']['ru_ixrss']
            resource_usage.integral_shared_memory = log_entry['lsfRusage']['ru_ismrss']
            resource_usage.integral_unshared_data = log_entry['lsfRusage']['ru_idrss']
            resource_usage.integral_unshared_stack = log_entry['lsfRusage']['ru_isrss']
            resource_usage.page_reclaims = log_entry['lsfRusage']['ru_minflt']
            resource_usage.page_faults = log_entry['lsfRusage']['ru_majflt']
            resource_usage.swaps = log_entry['lsfRusage']['ru_nswap']
            resource_usage.input_block_ops = log_entry['lsfRusage']['ru_inblock']
            resource_usage.output_block_ops = log_entry['lsfRusage']['ru_oublock']
            resource_usage.character_io_ops = log_entry['lsfRusage']['ru_ioch']
            resource_usage.messages_sent = log_entry['lsfRusage']['ru_msgsnd']
            resource_usage.messages_received = log_entry['lsfRusage']['ru_msgrcv']
            resource_usage.num_signals = log_entry['lsfRusage']['ru_nsignals']
            resource_usage.voluntary_context_switches = log_entry['lsfRusage']['ru_nvcsw']
            resource_usage.involuntary_context_switches = log_entry['lsfRusage']['ru_nivcsw']
            resource_usage.exact_user_time = log_entry['lsfRusage']['ru_exutime']
            resource_usage.attempt = attempt
            resource_usage.save()

        try:
            attempt.openlavaexitinfo
        except ObjectDoesNotExist:
            ol = OpenLavaExitInfo()
            ol.attempt = attempt
            ol.user_id = log_entry['userId']
            ol.user = user
            ol.begin_time = log_entry['beginTime']

            ol.termination_time = log_entry['termTime']
            ol.resource_request = log_entry['resReq']
            ol.cwd = log_entry['cwd']
            ol.input_file = log_entry['inFile']
            ol.output_file = log_entry['outFile']
            ol.error_file = log_entry['errFile']
            ol.input_file_spool = log_entry['inFileSpool']
            ol.command_spool = log_entry['commandSpool']
            ol.job_file = log_entry['jobFile']

            ol.resource_usage = resource_usage

            (project, created) = Project.objects.get_or_create(name=log_entry['projectName'])
            ol.project = project

            ol.host_factor = log_entry['hostFactor']
            ol.job_name = log_entry['jobName']
            ol.dependency_condition = log_entry['dependCond']
            ol.pre_execution_cmd = log_entry['preExecCmd']
            ol.email_user = log_entry['mailUser']
            ol.exit_status = log_entry['exitStatus']
            ol.max_num_processors = log_entry['maxNumProcessors']
            ol.login_shell = log_entry['loginShell']
            ol.array_index = log_entry['idx']
            ol.max_residual_mem = log_entry['maxRMem']
            ol.max_swap = log_entry['maxRSwap']
            ol.save()

            for state in OpenLavaSubmitOption.get_status_list(log_entry['options']):
                (o, created) = OpenLavaSubmitOption.objects.get_or_create(**state)
                ol.options.add(o)

            for host in log_entry['askedHosts']:
                (h, created) = Host.objects.get_or_create(name=host)
                ol.asked_hosts.add(h)
            ol.save()


# noinspection PyUnusedLocal
@cache_page(60 * 5)
def resource_data(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    """
    Generates resource usage data for the resource chart, this is the average of each field that is available on linux
    from AttemptResourceUsage.

    :param request: Request object
    :param start_time_js: Start time for the chart data, in milliseconds since epoch
    :param end_time_js: End time for the chart data, in milliseconds since epoch
    :param exclude_string: a string of options to exclude data
    :param filter_string: s string of options to filter data
    :param group_string: a string of fields to group by
    :return: json data object.

    """
    # Start time in milliseconds, rounded to nearest minute.
    start_time_js = int(int(start_time_js) / 60000) * 60000
    # End time in milliseconds, rounded to nearest minute.
    end_time_js = int(int(end_time_js) / 60000) * 60000

    # Attempts now contains all attempts that were active in this time period, ie, submitted before
    # the end and finished after the start time.
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)
    # From this point on, attempts is only used as part of the IN statement, it is essentially just a big list of
    # IDs that must be compared.

    # Group args is no amended so that all grouping is now relative to the AttemptResourceUsage table.
    group_args = group_string_to_group_args(group_string)
    group_args = ["attempt__%s" % a for a in group_args]

    resources = AttemptResourceUsage.objects.filter(attempt__in=attempts)

    if len(group_args) > 0:
        resources = resources.values(*group_args)
        resources = resources.annotate(
            Avg('user_time'),
            Avg('system_time'),
            Avg('max_rss'),
            Avg('page_reclaims'),
            Avg('page_faults'),
            Avg('input_block_ops'),
            Avg('output_block_ops'),
            Avg('voluntary_context_switches'),
            Avg('involuntary_context_switches'),
        )

        data = {}
        for row in resources:
            group_name = u""
            for n in group_args:
                if n == "attempt__status__exited_cleanly" and "attempt__status__name" in group_args:
                    continue
                if len(group_name) > 0:
                    group_name += u" "
                if n == "attempt__num_processors":
                    group_name += u"%s Processors" % row[n]
                elif n == "attempt__status__name":
                    group_name += u"%s (%s)" % (row[n], "Clean" if row['attempt__status__exited_cleanly'] else "Failed")
                else:
                    group_name += u"%s" % row[n]
            if group_name not in data:
                data[group_name] = {
                    'key': group_name,
                    'values': {
                        'user_time': 0,
                        'system_time': 0,
                        'max_rss': 0,
                        'page_reclaims': 0,
                        'page_faults': 0,
                        'input_block_ops': 0,
                        'output_block_ops': 0,
                        'voluntary_context_switches': 0,
                        'involuntary_context_switches': 0,
                    }
                }
            data[group_name]['values']['user_time'] += row['user_time__avg']
            data[group_name]['values']['system_time'] += row['system_time__avg']
            data[group_name]['values']['max_rss'] += row['max_rss__avg']
            data[group_name]['values']['page_reclaims'] += row['page_reclaims__avg']
            data[group_name]['values']['page_faults'] += row['page_faults__avg']
            data[group_name]['values']['input_block_ops'] += row['input_block_ops__avg']
            data[group_name]['values']['output_block_ops'] += row['output_block_ops__avg']
            data[group_name]['values']['voluntary_context_switches'] += row['voluntary_context_switches__avg']
            data[group_name]['values']['involuntary_context_switches'] += row['involuntary_context_switches__avg']
    else:
        resources = resources.aggregate(
            Avg('user_time'),
            Avg('system_time'),
            Avg('max_rss'),
            Avg('page_reclaims'),
            Avg('page_faults'),
            Avg('input_block_ops'),
            Avg('output_block_ops'),
            Avg('voluntary_context_switches'),
            Avg('involuntary_context_switches'),
        )

        data = {
            'Overall': {
                'key': 'Overall',
                'values': {
                    "user_time": resources['user_time__avg'],
                    "system_time": resources['system_time__avg'],
                    "max_rss": resources['max_rss__avg'],
                    "page_reclaims": resources['page_reclaims__avg'],
                    "page_faults": resources['page_faults__avg'],
                    "input_block_ops": resources['input_block_ops__avg'],
                    "output_block_ops": resources['output_block_ops__avg'],
                    "voluntary_context_switches": resources['voluntary_context_switches__avg'],
                    "involuntary_context_switches": resources['involuntary_context_switches__avg'],
                }
            }
        }
    data = sorted(data.values(), key=lambda val: val['key'])
    for series in data:
        series['values'] = [{'x': k, 'y': v} for k, v in series['values'].iteritems()]

    return create_js_success(data)


def consumption_bucket(attempts, group_args, req_start_time, req_end_time):
    # Where jobs start on or before, and end on or after, select sum_num_procs
    attempts = attempts.filter(start_time__lte=req_end_time, end_time__gte=req_start_time)

    duration = float(req_end_time - req_start_time)
    secs_in_hour = 60 * 60
    cpu_hours_per_block = float(duration / secs_in_hour)

    mins_after_start = "IF((start_time > %d), (%d - start_time), 0)" % (req_start_time, req_start_time)
    mins_before_end = "if( (end_time < %d) , (%d - end_time) , 0)" % (req_end_time, req_end_time)

    select = {
        "cpu_rate_for_block": "(SUM(num_processors*(%d+(%s)-(%s)))/3600/%f)" % (
        duration, mins_after_start, mins_before_end, cpu_hours_per_block),
        "cpu_for_block": "SUM(num_processors*(%d-(%s)-(%s)))" % (duration, mins_after_start, mins_before_end)
    }
    return attempts.extra(select=select).values(*group_args)


# noinspection PyUnusedLocal
@cache_page(60 * 5)
def cpu_consumption(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    """
    Generates CPU consumption data for the cpu usage chart.  CPU Usage is the cpu time for the given time period.

    :param request: Request object
    :param start_time_js: Start time for the chart data, in milliseconds since epoch
    :param end_time_js: End time for the chart data, in milliseconds since epoch
    :param exclude_string: a string of options to exclude data
    :param filter_string: s string of options to filter data
    :param group_string: a string of fields to group by
    :return: json data object.

    """
    # Start time in milliseconds, rounded to nearest minute.
    start_time_js = int(int(start_time_js) / 60000) * 60000
    start_time_ep = start_time_js / 1000
    # End time in milliseconds, rounded to nearest minute.
    end_time_js = int(int(end_time_js) / 60000) * 60000
    end_time_ep = end_time_js / 1000
    # Attempts now contains all attempts that were active in this time period, ie, submitted before
    # the end and finished after the start time.
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string, no_times=True)

    # Attempts now only contains the exact data needed to perform the query, no other data is retrieved.
    # This should in the best case only require data from a single table.
    group_args = group_string_to_group_args(group_string)

    # we want about 500 data points...

    duration = end_time_ep - start_time_ep
    timestep = duration / 600
    nice_timesteps = [
        1,  # Per Second
        60,  # One Minute Intervals
        120,  # Two Minute Intervals
        1200,  # Twenty Minute Intervals
        3600,  # Hourly
        7200,  # 2 Hours
        14400,  # 4 Hours
        28800,  # 8 Hours
        86400,  # 1 day
        172800,  # 2 day
        345600,  # 4 day
        604800,  # week
        20160 * 60,  # 2 weeks.
    ]
    for possible_timestep in nice_timesteps:
        if duration / possible_timestep < 600:
            timestep = possible_timestep
            break

    times = range(start_time_ep, end_time_ep, timestep)

    # Populate serieses with all possible series names
    series_names = ["Overall"]
    if len(group_args) > 0:
        series_names = []
        for s in attempts.values(*group_args).distinct():
            group_name = u""
            for n in group_args:
                if len(group_name) > 0:
                    group_name += u" "
                group_name += u"%s" % s[n]
            series_names.append(group_name)

    serieses = {}
    for name in series_names:
        serieses[name] = {
            'key': name,
            'values': {}
        }
        for time_value in times:
            serieses[name]['values'][time_value] = {'x': time_value * 1000, 'y': 0}

    for start_time in times:
        end_time = start_time + timestep
        args = group_args + ["cpu_rate_for_block"]
        for row in consumption_bucket(attempts, args, start_time, end_time):
            group_name = u"Overall"
            if len(group_args) > 0:
                group_name = u""
                for n in group_args:
                    if len(group_name) > 0:
                        group_name += u" "
                    group_name += u"%s" % row[n]

            if row['cpu_rate_for_block']:
                serieses[group_name]['values'][start_time]['y'] += int(row['cpu_rate_for_block'])

    for s in serieses.itervalues():
        s['values'] = sorted(s['values'].values(), key=lambda x: x['x'])
    return create_js_success(sorted(serieses.values(), key=lambda a: a['key']), message="")


# noinspection PyUnusedLocal
@cache_page(60 * 5)
def utilization_data(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    """
    Generates utilization data for the utilization chart, this is essentially number of processors requested, vs
    number of processors that are in use, for the given time period. Grouped by zero or more fields.

    :param request: Request object
    :param start_time_js: Start time for the chart data, in milliseconds since epoch
    :param end_time_js: End time for the chart data, in milliseconds since epoch
    :param exclude_string: a string of options to exclude data
    :param filter_string: s string of options to filter data
    :param group_string: a string of fields to group by
    :return: json data object.

    """

    # TODO: This can be significantly improved by using an aggregate function, first calculate the desired
    # timesteps, then for each timestep filter on jobs that are running, then jobs that are pending.
    # This wasnt possible until the addition of submit/start/end times to attempts which makes this now a trivial
    # operation

    # Start time in milliseconds, rounded to nearest minute.
    start_time_js = int(int(start_time_js) / 60000) * 60000
    # End time in milliseconds, rounded to nearest minute.
    end_time_js = int(int(end_time_js) / 60000) * 60000

    # Attempts now contains all attempts that were active in this time period, ie, submitted before
    # the end and finished after the start time.
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)

    # Attempts now only contains the exact data needed to perform the query, no other data is retrieved.
    # This should in the best case only require data from a single table.
    group_args = group_string_to_group_args(group_string)

    required_values = ["num_processors", "submit_time", "start_time", "end_time"] + group_args
    attempts = attempts.values(*required_values)

    # Unique list of times that are used, for smaller datasets, this is the best possible list of times to use.
    times = set()
    times.add(start_time_js)
    times.add(end_time_js)

    # Dict containing each series.
    serieses = {}
    for at in attempts:
        submit_time = at['submit_time'] * 1000
        start_time = at['start_time'] * 1000
        end_time = at['end_time'] * 1000
        times.add(submit_time)
        times.add(start_time)
        times.add(end_time)
        times.add(submit_time - 1)
        times.add(start_time - 1)
        times.add(end_time - 1)
        np = at['num_processors']

        group_name = u""
        for n in group_args:
            if len(group_name) > 0:
                group_name += u" "
            group_name += u"%s" % at[n]

        pend_series = u"%s Pending" % group_name
        run_series = u"%s running" % group_name
        if pend_series not in serieses:
            serieses[pend_series] = {'key': pend_series, 'values': {}}
        pend_series = serieses[pend_series]['values']

        if run_series not in serieses:
            serieses[run_series] = {'key': run_series, 'values': {}}
        run_series = serieses[run_series]['values']

        if submit_time - 1 not in pend_series:
            pend_series[submit_time - 1] = 0

        if submit_time in pend_series:
            pend_series[submit_time] += np
        else:
            pend_series[submit_time] = np

        if start_time - 1 not in pend_series:
            pend_series[start_time - 1] = 0

        if start_time in pend_series:
            pend_series[start_time] -= np
        else:
            pend_series[start_time] = -1 * np

        if start_time - 1 not in run_series:
            run_series[start_time - 1] = 0

        if start_time in run_series:
            run_series[start_time] += np
        else:
            run_series[start_time] = np

        if end_time - 1 not in run_series:
            run_series[end_time - 1] = 0

        if end_time in run_series:
            run_series[end_time] -= np
        else:
            run_series[end_time] = -1 * np
    if len(times) > 2000:
        step_size = ((end_time_js - start_time_js) / 1000)
        step_size = int(step_size / 30000)
        if step_size < 0:
            step_size = 1
        step_size *= 30000  # Multiple of 30 seconds....
        times = range(start_time_js, end_time_js, step_size)
    else:
        times = sorted(times)
    # Serieses now contains an item for each series we need to chart
    for s in serieses.itervalues():
        values = s['values']
        total = 0
        ts = []
        vs = []
        for time_value in times:
            if time_value not in values:
                values[time_value] = 0
        for time_value in sorted(values.keys()):
            total += values[time_value]
            ts.append(time_value)
            vs.append(total)
        f = interp1d(ts, vs, copy=False, bounds_error=False, fill_value=0)
        s['values'] = [{'x': time_value, 'y': float(f(time_value))} for time_value in times]
    return create_js_success(sorted(serieses.values(), key=lambda a: a['key']), message="")


def get_attempts(start_time_js, end_time_js, exclude_string, filter_string, no_times=False):
    """

    Gets all attempts that are active between the specified time periods, after
    having applied the filters and exclude options.

    :param start_time_js: Start time for the chart data, in milliseconds since epoch
    :param end_time_js: End time for the chart data, in milliseconds since epoch
    :param exclude_string: a string of options to exclude data
    :param filter_string: s string of options to filter data
    :return: Queryset

    """
    filter_args = filter_string_to_params(filter_string)
    exclude_args = filter_string_to_params(exclude_string)
    attempts = Attempt.objects.all()
    if no_times is False:
        if start_time_js:
            start_time = int(int(start_time_js) / 1000)
            attempts = attempts.filter(end_time__gte=start_time)
        if end_time_js:
            end_time = int(int(end_time_js) / 1000)
            attempts = attempts.filter(submit_time__lte=end_time)
    for key, val in filter_args.items():
        attempts = attempts.filter(**{key: val})
    for key, val in exclude_args.items():
        attempts = attempts.exclude(**{key: val})
    return attempts


@cache_page(60 * 5)
def utilization_table(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    """
    Generates utilization table for the utilization table

    :param request: Request object
    :param start_time_js: Start time for the chart data, in milliseconds since epoch, rounded to the nearest minute
    :param end_time_js: End time for the chart data, in milliseconds since epoch, rounded to the nearest minute
    :param exclude_string: a string of options to exclude data
    :param filter_string: s string of options to filter data
    :param group_string: a string of fields to group by
    :return: json data object.

    """
    # Start time in milliseconds, rounded to nearest minute.
    start_time_js = int(int(start_time_js) / 60000) * 60000
    # End time in milliseconds, rounded to nearest minute.
    end_time_js = int(int(end_time_js) / 60000) * 60000

    # Attempts now contains all attempts that were active in this time period, ie, submitted before
    # the end and finished after the start time.
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)

    # Attempts now only contains the exact data needed to perform the query, no other data is retrieved.
    # This should in the best case only require data from a single table.

    group_args = group_string_to_group_args(group_string)
    annotations = []
    aggs = ['pend_time', 'wall_time', 'cpu_time']
    for i in aggs:
        annotations.append(Avg(i))
        annotations.append(Min(i))
        annotations.append(Max(i))
        annotations.append(Sum(i))

    rows = []
    header = []
    if len(group_args) > 0:
        attempts = attempts.values(*group_args)
        nice_names = {}
        for val in FILTER_FIELDS:
            nice_names[val['filter_string']] = val['display_name']
        for a in group_args:
            field = {'name': a}
            if a in nice_names:
                field['nice_name'] = nice_names[a]
            else:
                field['nice_name'] = a
            header.append(field)

        for r in attempts.annotate(*annotations):
            row = {
                'groups': []
            }
            for field in group_args:
                f = dict()
                f['name'] = field
                if field in nice_names:
                    f['nice_name'] = nice_names[field]
                else:
                    f['nice_name'] = field

                f['value'] = r[field]
                row['groups'].append(f)

            for a in aggs:
                for i in ["avg", "min", "max", "sum"]:
                    name = "%s__%s" % (a, i)
                    row[name] = datetime.timedelta(seconds=int(r[name]))

            rows.append(row)
    else:

        r = attempts.aggregate(*annotations)
        row = {
        }
        for a in aggs:
            for i in ["avg", "min", "max", "sum"]:
                name = "%s__%s" % (a, i)
                try:
                    row[name] = datetime.timedelta(seconds=int(r[name]))
                except TypeError:
                    row[name] = datetime.timedelta(seconds=0)
        rows.append(row)
    return render(request, "lavaFlow/widgets/utilization_chart.html", {'header': header, 'rows': rows})


# noinspection PyUnusedLocal
@cache_page(60 * 5)
def consumption_bar_data(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    """
    Generates consumption data for the consumption chart, this is a total of CPU time, wall time, pend time and the
    total number of tasks started during this time grouped by whatever the user requires.  To make reports clearer
    when the user requests num_processors, or exit state, these are made human readable.

    :param request: Request object

    :param start_time_js:

        Start time for the chart data, in milliseconds since epoch, this is converted to the nearest minute

    :param end_time_js:

        End time for the chart data, in milliseconds since epoch, this is converted to the nearest minute

    :param exclude_string: a string of options to exclude data

    :param filter_string: s string of options to filter data

    :param group_string: a string of fields to group by

    :return: json data object.

    """
    # Start time in milliseconds, rounded to nearest minute.
    start_time_js = int(int(start_time_js) / 60000) * 60000
    # end time in milliseconds
    end_time_js = int(int(end_time_js) / 60000) * 60000

    # Attempts now contains all attempts that were active in this time period, ie, submitted before
    # the end and finished after the start time.
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)

    # Attempts now only contains the exact data needed to perform the query, no other data is retrieved.
    # This should in the best case only require data from a single table.
    group_args = group_string_to_group_args(group_string)
    if "status__name" in group_args and "status__exited_cleanly" not in group_args:
        group_args.append("status__exited_cleanly")
    if len(group_args) > 0:
        attempts = attempts.values(*group_args)
        attempts = attempts.annotate(Sum('pend_time'), Sum('wall_time'), Sum('cpu_time'), Count('num_processors'))

        data = {}
        for row in attempts:
            group_name = u""
            for n in group_args:
                if n == "status__exited_cleanly" and "status__name" in group_args:
                    continue
                if len(group_name) > 0:
                    group_name += u" "
                if n == "num_processors":
                    group_name += u"%s Processors" % row[n]
                elif n == "status__name":
                    group_name += u"%s (%s)" % (row[n], "Clean" if row['status__exited_cleanly'] else "Failed")
                else:
                    group_name += u"%s" % row[n]
            if len(group_name) < 1:
                group_name = "Total"
            if group_name not in data:
                data[group_name] = {
                    'key': group_name,
                    'values': {
                        "Sum CPU": 0,
                        "Sum Wall": 0,
                        "Sum Pend": 0,
                        "Total Tasks": 0
                    }
                }
            data[group_name]['values']['Sum CPU'] += row['cpu_time__sum']
            data[group_name]['values']['Sum Wall'] += row['wall_time__sum']
            data[group_name]['values']['Sum Pend'] += row['pend_time__sum']
            data[group_name]['values']['Total Tasks'] += row['num_processors__count']

    else:
        attempts = attempts.aggregate(Sum('pend_time'), Sum('wall_time'), Sum('cpu_time'), Count('num_processors'))
        data = {
            'Overall': {
                'key': 'Overall',
                'values': {
                    "Sum CPU": attempts['cpu_time__sum'],
                    "Sum Wall": attempts['wall_time__sum'],
                    "Sum Pend": attempts['pend_time__sum'],
                    "Total Tasks": attempts['num_processors__count'],
                }
            }
        }
    data = sorted(data.values(), key=lambda val: val['key'])
    for series in data:
        series['values'] = [{'x': k, 'y': v} for k, v in series['values'].iteritems()]

    return create_js_success(data)


@cache_page(60 * 5)
def submission_bar_data(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    """
    Generates chart data for the submission chart, this shows when jobs are being submitted into the cluster.

    :param request: Request object

    :param start_time_js:

        Start time for the chart data, in milliseconds since epoch, this is converted to the nearest minute

    :param end_time_js:

        End time for the chart data, in milliseconds since epoch, this is converted to the nearest minute

    :param exclude_string: a string of options to exclude data

    :param filter_string: s string of options to filter data

    :param group_string: a string of fields to group by

    :return: json data object.

    """
    field = request.GET.get("field", "submit_hour_of_day")
    fields_to_friendly = {
        "submit_hour_of_day": {
            0: "00:00",
            1: "01:00",
            2: "02:00",
            3: "03:00",
            4: "04:00",
            5: "05:00",
            6: "06:00",
            7: "07:00",
            8: "08:00",
            9: "09:00",
            10: "10:00",
            11: "11:00",
            12: "12:00",
            13: "13:00",
            14: "14:00",
            15: "15:00",
            16: "16:00",
            17: "17:00",
            18: "18:00",
            19: "19:00",
            20: "20:00",
            21: "21:00",
            22: "22:00",
            23: "23:00",
        },
        "submit_day_of_week": {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        },
        "submit_day_of_month": {
        },
        "submit_week_of_year": {
        },
        "submit_month": {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }
    }
    for i in range(1, 32):
        fields_to_friendly["submit_day_of_month"][i] = i
    for i in range(1, 54):
        fields_to_friendly["submit_week_of_year"][i] = "Week: %s" % i

    # Start time in milliseconds, rounded to nearest minute.
    start_time_js = int(int(start_time_js) / 60000) * 60000
    # End time in milliseconds, rounded to nearest minute.
    end_time_js = int(int(end_time_js) / 60000) * 60000

    # Attempts now contains all attempts that were active in this time period, ie, submitted before
    # the end and finished after the start time.
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)
    # From this point on, attempts is only used as part of the IN statement, it is essentially just a big list of
    # IDs that must be compared.

    # Group args is no amended so that all grouping is now relative to the AttemptResourceUsage table.
    group_args = group_string_to_group_args(group_string)
    group_args = ["attempt__%s" % a for a in group_args]

    jobs = Job.objects.filter(attempt__pk__in=attempts).distinct()
    vargs = group_args + [field]

    jobs = jobs.values(*vargs)

    jobs = jobs.annotate(
        Count('job_id'),
    )

    data = {}
    for row in jobs:
        group_name = u""
        for n in group_args:
            if n == "attempt__status__exited_cleanly" and "attempt__status__name" in group_args:
                continue
            if len(group_name) > 0:
                group_name += u" "
            if n == "attempt__num_processors":
                group_name += u"%s Processors" % row[n]
            elif n == "attempt__status__name":
                group_name += u"%s (%s)" % (row[n], "Clean" if row['attempt__status__exited_cleanly'] else "Failed")
            else:
                group_name += u"%s" % row[n]
        if len(group_name) < 1:
            group_name = u"Overall"
        if group_name not in data:
            data[group_name] = {
                'key': group_name,
                'values': {}
            }
            for k in fields_to_friendly[field].keys():
                data[group_name]['values'][k] = 0

        data[group_name]['values'][int(row[field])] += row['job_id__count']
    data = sorted(data.values(), key=lambda val: val['key'])
    for series in data:
        vals = []
        for entry in sorted([{'x': k, 'y': v} for k, v in series['values'].iteritems()], key=lambda val: val['x']):
            vals.append({
                'x': fields_to_friendly[field][entry['x']],
                'y': entry['y']
            })
        series['values'] = vals

    return create_js_success(data)


# noinspection PyUnusedLocal
@cache_page(60 * 5)
def utilization_view(request, start_time_js=None, end_time_js=None, exclude_string="none", filter_string="none",
                     group_string=""):
    """

    Renders and displays the utilization view page.

    :param request: Request object passed by django.
    :param start_time_js: Start time for the chart data, in milliseconds since epoch
    :param end_time_js: End time for the chart data, in milliseconds since epoch
    :param exclude_string: a string of options to exclude data
    :param filter_string: s string of options to filter data
    :param group_string: a string of fields to group data by.
    :return: Rendered HTML page.

    """

    times = Attempt.objects.aggregate(last_end_time=Max('end_time'), first_start_time=Min('start_time'))

    first_start_time_js = 0
    if times['first_start_time']:
        first_start_time_js = times['first_start_time'] * 1000

    last_end_time_js = 0
    if times['last_end_time']:
        last_end_time_js = times['last_end_time'] * 1000

    if end_time_js is None:
        end_time_js = 0
    end_time_js = int(end_time_js)
    if start_time_js is None:
        start_time_js = 0
    start_time_js = int(start_time_js)

    if end_time_js == 0:
        print "setting to end"
        end_time_js = last_end_time_js

    if start_time_js == 0:
        print "setting_to_start"
        start_time_js = end_time_js - (7 * 86400 * 1000)
        if start_time_js < first_start_time_js:
            print "clipping..."
            start_time_js = first_start_time_js

    fs = {

    }
    for f in FILTER_FIELDS:
        f['values'] = []
        f['filter'] = {
            'in': [],
            'lt': None,
            'gt': None,
            'lte': None,
            'gte': None,
        }
        f['exclude'] = {
            'in': [],
            'lt': None,
            'gt': None,
            'lte': None,
            'gte': None,
        }
        fs[f['filter_string']] = f
    set_filters('filter', filter_string, fs)
    set_filters('exclude', exclude_string, fs)
    data = {
        'first_start_time_js': first_start_time_js,
        'last_end_time_js': last_end_time_js,
        'build_filter_url': reverse('lf_build_filter'),
        'start_time': start_time_js,
        'end_time': end_time_js,
        'current_filters': json.dumps(fs),
        'filter_list': FILTER_FIELDS,
        'first_filter': FILTER_FIELDS[0]['filter_string']
    }
    return render(request, "lavaFlow/utilization_view.html", data)


# noinspection PyUnusedLocal,PyUnusedLocal
@cache_page(60 * 5)
def util_total_attempts(request, start_time_js=None, end_time_js=None, exclude_string="", filter_string="",
                        group_string=""):
    start_time_js = int(start_time_js)
    end_time_js = int(end_time_js)
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)
    count = attempts.count()
    data = {
        'count': count,
    }
    return create_js_success(data)


def group_string_to_group_args(group_string):
    if group_string == "none":
        return []
    group_args = []
    if len(group_string) > 0:
        group_args = group_string.split("/")
    return group_args


def filter_string_to_params(filter_string):
    # Build the additional filters
    if len(filter_string) < 1 or filter_string == "none":
        return {}
    filter_args = {}
    for f in filter_string.split("/"):
        (ftr, dot, value) = f.partition(".")
        if ftr.endswith("__in"):  # multi value...
            if ftr not in filter_args:
                filter_args[ftr] = []
            filter_args[ftr].append(value)
        else:
            filter_args[ftr] = value
    return filter_args


def set_filters(field, filter_string, structure):
    if len(filter_string) < 1 or filter_string == "none":
        return
    for f in filter_string.split("/"):
        (ftr, dot, value) = f.partition(".")
        (ftr, uu, operator) = ftr.rpartition("__")

        if operator == "in" and value not in structure[ftr][field][operator]:
            structure[ftr][field][operator].append(value)
        else:
            structure[ftr][field][operator] = value


@csrf_exempt
def build_filter(request):
    data = json.loads(request.body)

    view = data['view']
    start_time_js = data['start_time_js']
    if start_time_js < 0:
        start_time_js = 0
    end_time_js = data['end_time_js']
    if end_time_js < 0:
        end_time_js = 0

    values = []
    for value in data['filters']:
        field = value['field']
        operator = value['operator']
        value = value['value']
        if operator == 'in':
            values.extend(["%s__in.%s" % (field, val) for val in value])
        else:
            values.append("%s__%s.%s" % (field, operator, value))

    filter_string = "/".join(values)
    if len(filter_string) < 1:
        filter_string = "none"

    values = []
    for value in data['excludes']:
        field = value['field']
        operator = value['operator']
        value = value['value']
        if operator == 'in':
            values.extend(["%s__in.%s" % (field, val) for val in value])
        else:
            values.append("%s__%s.%s" % (field, operator, value))

    exclude_string = "/".join(values)
    if len(exclude_string) < 1:
        exclude_string = "none"

    group_string = "/".join(data['groups'])
    if len(group_string) < 1:
        group_string = "none"

    if view == 'lf_get_report_range':
        url = reverse(view, kwargs={'exclude_string': str(exclude_string), 'filter_string': str(filter_string)})
    else:
        url = reverse(view, kwargs={'start_time_js': int(start_time_js), 'end_time_js': int(end_time_js),
                                    'exclude_string': str(exclude_string), 'filter_string': str(filter_string),
                                    'group_string': str(group_string)})
    url = request.build_absolute_uri(url)

    return HttpResponse(json.dumps({'url': url}), content_type="application/json")


def get_field_values(request):
    """
    Gets a distinct list of values for a single specified field.

    If the field is not in FILTER_LIST then bad request is returned

    :param request: Request Object
    :return: JSON array of values

    """
    field = request.GET.get("field", None)

    if not field:
        return create_js_bad_request(message="field and model parameters must be present")
    if field not in [f['filter_string'] for f in FILTER_FIELDS]:
        return create_js_bad_request(message="Field not in filter_fields")

    conversions = {}
    for f in FILTER_FIELDS:
        if 'conversion' in f:
            conversions[f['filter_string']] = f['conversion']
    data = {'values': []}
    for row in Attempt.objects.values(field).distinct():
        data['values'].append({
            'value': row[field],
            'display_value': get_friendly_val(conversions[field], row[field]) if field in conversions else row[field],
        })

        data['values'].sort(key=lambda x: x['value'])
    return create_js_success(data)
