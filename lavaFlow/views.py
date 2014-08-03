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
import datetime
import json
import logging

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from django.db.models import Avg, Count, Sum
from django.views.generic import ListView
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.middleware.csrf import get_token
from scipy.interpolate import interp1d

from lavaFlow.models import *

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
            'description': "The running job was suspended by the system because an execution host was overloaded or the queue run window closed.",
        },
        0x10: {
            'friendly': "Suspended by user",
            'name': "JOB_STAT_USUSP",
            'description': "The running job was suspended by its owner or the LSF system administrator.",
        },
        0x20: {
            'friendly': "Exited",
            'name': "JOB_STAT_EXIT",
            'description': "The job has terminated with a non-zero status - it may have been aborted due to an error in its execution, or killed by its owner or by the LSF system administrator.",
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
            'description': "The slave batch daemon (sbatchd) on the host on which the job is processed has lost contact with the master batch daemon (mbatchd).",
        },
    }


log = logging.getLogger(__name__)

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
    data={
        'status':"OK",
        'data':data,
        'message':message,
    }
    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
def gridengine_import(request, cluster_name):

    data = json.loads(request.body)
    (cluster, created) = Cluster.objects.get_or_create(name=cluster_name)
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
            'description': 'qmaster asked about an unknown job (Not in accounting)',
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
            'name': 'qmaster enforced h_rt, h_cpu, or h_vmem limit',
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
            'description': 'ran, but killed by a signal (perhaps due to exceeding resources), task died, shepherd died (e.g. node crash), etc.',
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
        r.charecter_io_ops = -1
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
        a.catagory = ""
        if data['catagory']:
            a.catagory = data['catagory']
        a.io_wait = data['iow']
        a.pe_task_id = data['pe_taskid']
        a.max_vmem = data['maxvmem']
        a.advanced_reservation_id = data['arid']
        a.advanced_reservation_submit_time = data['ar_submission_time']
        a.save()
    return HttpResponse("OK", content_type="text/plain")


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
    log = event['eventLog']['jobFinishLog']

    (user, created) = User.objects.get_or_create(name=log['userName'])
    (submit_host, created) = Host.objects.get_or_create(name=log['fromHost'])
    (job, created) = Job.objects.get_or_create(
        cluster=cluster,
        job_id=log['jobId'],
        user=user,
        submit_host=submit_host,
        submit_time=log['submitTime'])

    (task, created) = Task.objects.get_or_create(cluster=cluster, job=job, user=user, task_id=log['idx'])
    num_processors = log['numProcessors']
    start_time = log['startTime']
    if start_time == 0:  # Job was killed before starting
        start_time = event['eventTime']

    end_time = event['eventTime']

    wall_time = end_time - start_time
    cpu_time = wall_time * num_processors
    pend_time = event['eventTime'] - log['submitTime']

    if start_time > 0:  # 0 == job didn't start
        pend_time = start_time - log['submitTime']

    (queue, created) = Queue.objects.get_or_create(name=log['queue'], cluster=cluster)

    job_state = OPENLAVA_JOB_STATES[log['jStatus']]
    clean = False
    if job_state['name'] == "JOB_STAT_DONE":
        clean = True
    (status, created) = JobStatus.objects.get_or_create(
        code=log['jStatus'],
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
            'command': log['command'],
        },
    )

    if created:
        for host in log['execHosts']:
            (execution_host, created) = Host.objects.get_or_create(name=host)
            attempt.execution_hosts.add(execution_host)

        (project, created) = Project.objects.get_or_create(name=log['projectName'])
        attempt.projects.add(project)

        try:
            attempt.attemptresourceusage
        except ObjectDoesNotExist:
            resource_usage = AttemptResourceUsage()
            resource_usage.user_time = log['lsfRusage']['ru_utime']
            resource_usage.system_time = log['lsfRusage']['ru_stime']
            resource_usage.max_rss = log['lsfRusage']['ru_maxrss']
            resource_usage.integral_shared_text = log['lsfRusage']['ru_ixrss']
            resource_usage.integral_shared_memory = log['lsfRusage']['ru_ismrss']
            resource_usage.integral_unshared_data = log['lsfRusage']['ru_idrss']
            resource_usage.integral_unshared_stack = log['lsfRusage']['ru_isrss']
            resource_usage.page_reclaims = log['lsfRusage']['ru_minflt']
            resource_usage.page_faults = log['lsfRusage']['ru_majflt']
            resource_usage.swaps = log['lsfRusage']['ru_nswap']
            resource_usage.input_block_ops = log['lsfRusage']['ru_inblock']
            resource_usage.output_block_ops = log['lsfRusage']['ru_oublock']
            resource_usage.charecter_io_ops = log['lsfRusage']['ru_ioch']
            resource_usage.messages_sent = log['lsfRusage']['ru_msgsnd']
            resource_usage.messages_received = log['lsfRusage']['ru_msgrcv']
            resource_usage.num_signals = log['lsfRusage']['ru_nsignals']
            resource_usage.voluntary_context_switches = log['lsfRusage']['ru_nvcsw']
            resource_usage.involuntary_context_switches = log['lsfRusage']['ru_nivcsw']
            resource_usage.exact_user_time = log['lsfRusage']['ru_exutime']
            resource_usage.attempt = attempt
            resource_usage.save()

        try:
            attempt.openlavaexitinfo
        except ObjectDoesNotExist:
            ol = OpenLavaExitInfo()
            ol.attempt = attempt
            ol.user_id = log['userId']
            ol.user = user
            ol.begin_time = log['beginTime']

            ol.termination_time = log['termTime']
            ol.resource_request = log['resReq']
            ol.cwd = log['cwd']
            ol.input_file = log['inFile']
            ol.output_file = log['outFile']
            ol.error_file = log['errFile']
            ol.input_file_spool = log['inFileSpool']
            ol.command_spool = log['commandSpool']
            ol.job_file = log['jobFile']

            ol.resource_usage = resource_usage

            (project, created) = Project.objects.get_or_create(name=log['projectName'])
            ol.project = project

            ol.host_factor = log['hostFactor']
            ol.job_name = log['jobName']
            ol.dependency_condition = log['dependCond']
            ol.pre_execution_cmd = log['preExecCmd']
            ol.email_user = log['mailUser']
            ol.exit_status = log['exitStatus']
            ol.max_num_processors = log['maxNumProcessors']
            ol.login_shell = log['loginShell']
            ol.array_index = log['idx']
            ol.max_residual_mem = log['maxRMem']
            ol.max_swap = log['maxRSwap']
            ol.save()

            for state in OpenLavaSubmitOption.get_status_list(log['options']):
                (o, created) = OpenLavaSubmitOption.objects.get_or_create(**state)
                ol.options.add(o)

            for host in log['askedHosts']:
                (h, created) = Host.objects.get_or_create(name=host)
                ol.asked_hosts.add(h)
            ol.save()


def get_attempts(start_time_js, end_time_js, exclude_string, filter_string):
    filter_args = filter_string_to_params(filter_string)
    exclude_args = filter_string_to_params(exclude_string)
    attempts = Attempt.objects.all()
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


@cache_page(60 * 60 * 2)
def utilization_table(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    start_time_js = int(start_time_js)
    end_time_js = int(end_time_js)
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)
    group_args = group_string_to_group_args(group_string)
    if len(group_args) > 0:
        attempts = attempts.values(*group_args)
    annotations = []
    aggs = ['pend_time', 'wall_time', 'cpu_time']
    for i in aggs:
        annotations.append(Avg(i))
        annotations.append(Min(i))
        annotations.append(Max(i))
        annotations.append(Sum(i))
    rows = []
    header = []
    nice_names = {
        'num_processors': "Num Slots",
        'cluster__name': "Cluster",
        'status__name': "Exit Reason",
    }
    for a in group_args:
        field = {}
        field['name'] = a
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
            f = {}
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

    return render(request, "lavaFlow/widgets/utilization_chart.html", {'header': header, 'rows': rows})


def utilization_bar_size(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    start_time_js = int(start_time_js)
    end_time_js = int(end_time_js)
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)
    data = []
    for row in attempts.values('num_processors').annotate(Sum('pend_time'), Sum('wall_time'), Sum('cpu_time'),
                                                          Count('num_processors')).order_by('num_processors'):
        data.append({
            'key': "%s Processors" % row['num_processors'],
            'values': [
                {
                    'x': "Sum CPU",
                    'y': row['cpu_time__sum'],
                },
                {
                    'x': "Sum Wall",
                    'y': row['wall_time__sum'],
                },
                {
                    'x': "Sum Pend",
                    'y': row['pend_time__sum'],
                },
                {
                    'x': "Total Tasks",
                    'y': row['num_processors__count'],
                },
            ]
        })

    return HttpResponse(json.dumps(data, indent=3, sort_keys=True), content_type="application/json")


def utilization_bar_exit(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    start_time_js = int(start_time_js)
    end_time_js = int(end_time_js)
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)
    data = []
    for row in attempts.values('status__exited_cleanly', 'status__name').annotate(Sum('pend_time'), Sum('wall_time'),
                                                                                  Sum('cpu_time'),
                                                                                  Count('num_processors')).order_by(
            'num_processors'):
        if row['status__exited_cleanly'] == True:
            clean = "Success"
        else:
            clean = "Failed"
        data.append({
            'key': "%s (%s)" % ( row['status__name'], clean    ),
            'values': [
                {
                    'x': "Sum CPU",
                    'y': row['cpu_time__sum'],
                },
                {
                    'x': "Sum Wall",
                    'y': row['wall_time__sum'],
                },
                {
                    'x': "Sum Pend",
                    'y': row['pend_time__sum'],
                },
                {
                    'x': "Total Tasks",
                    'y': row['num_processors__count'],
                },
            ]
        })

    return HttpResponse(json.dumps(data, indent=3, sort_keys=True), content_type="application/json")


# @cache_page(60 * 60 * 2)
def utilization_data(request, start_time_js=0, end_time_js=0, exclude_string="", filter_string="", group_string=""):
    # Start time in milliseconds
    start_time_js = int(start_time_js)
    # Start time in seconds
    start_time_ep = int(start_time_js / 1000)
    # end time in milliseconds
    end_time_js = int(end_time_js)
    # end time in seconds
    end_time_ep = int(end_time_js / 1000)

    # Attempts now contains all attempts that were active in this time period, ie, submitted before
    # the end and finished after the start time.
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)

    # Attempts now only contains the exact data needed to perform the query, no other data is retrieved.
    # This should in the best case only require data from a single table.
    group_args = group_string_to_group_args(group_string)
    # Always need to have num_processors so they can be counted.
    group_args.append("num_processors")
    group_args.append("submit_time")
    group_args.append("start_time")
    group_args.append("end_time")
    attempts = attempts.values(*group_args)

    # Unique list of times that are used, for smaller datasets, this is the best possible list of times to use.
    times=set()
    times.add(start_time_js)
    times.add(end_time_js)

    # Dict containing each series.
    serieses={}
    for at in attempts:
        submit_time = at['submit_time'] * 1000
        start_time = at['start_time'] * 1000
        end_time = at['end_time'] * 1000
        times.add(submit_time)
        times.add(start_time)
        times.add(end_time)
        np=at['num_processors']

        group_name = u""
        for n in group_args:
            if len(group_name) > 0:
                group_name += u" "
            group_name += n
            pend_series=u"%s Pending" % group_name
            run_series=u"%s running" % group_name
            if pend_series not in serieses:
                serieses[pend_series]={'key': pend_series, 'values':{}}
            pend_series=serieses[pend_series]['values']

            if run_series not in serieses:
                serieses[run_series]={'key': run_series, 'values':{}}
            run_series=serieses[run_series]['values']

            if submit_time  in pend_series:
                pend_series[submit_time] += np
            else:
                pend_series[submit_time] = np

            if start_time in pend_series:
                pend_series[start_time] -= np
            else:
                pend_series[start_time] = -1 * np

            if start_time in run_series:
                run_series[start_time] += np
            else:
                run_series[start_time] = np
            if end_time in run_series:
                run_series[end_time] -= np
            else:
                run_series[end_time] = -1 * np

    times=sorted(times)
    # Serieses now contains an item for each series we need to chart
    for s in serieses.itervalues():
        values=s['values']
        total=0
        ts=[]
        vs=[]
        for time in sorted(values.keys()):
            total += values[time]
            ts.append(time)
            vs.append(total)
        s['f']=interp1d(ts, vs, copy=False, bounds_error=False, fill_value=0)
        s['values']=[{'x':time, 'y':float(s['f'](time))} for time in times]

    return HttpResponse(json.dumps(serieses.values(), indent=1), content_type="application/json")


@cache_page(60 * 60 * 2)
def utilization_view(request, start_time_js=None, end_time_js=None, exclude_string="none", filter_string="none",
                     group_string=""):
    #
    if start_time_js == None:
        start_time_js = -1
    if end_time_js == None:
        end_time_js = -1

    data = {
        'filters': json.dumps(filter_string_to_params(filter_string)),
        'excludes': json.dumps(filter_string_to_params(exclude_string)),
        'report_range_url': reverse('lf_get_report_range',
                                    kwargs={'filter_string': filter_string, 'exclude_string': exclude_string}),
        'build_filter_url': reverse('lf_build_filter'),
        'start_time': start_time_js,
        'end_time': end_time_js,
    }
    return render(request, "lavaFlow/utilization_view.html", data)


def util_total_attempts(request, start_time_js=None, end_time_js=None, exclude_string="", filter_string="",
                        group_string=""):
    start_time_js = int(start_time_js)
    end_time_js = int(end_time_js)
    attempts = get_attempts(start_time_js, end_time_js, exclude_string, filter_string)
    count = attempts.count()
    data = {
        'count': count,
    }
    return HttpResponse(json.dumps(data), content_type="application/json")


def util_report_range(request, exclude_string="", filter_string=""):
    ONE_DAY = 24 * 60 * 60 * 60  # 1 day in seconds
    filter_args = filter_string_to_params(filter_string)
    exclude_args = filter_string_to_params(exclude_string)
    attempts = Attempt.objects.all()
    for key, val in filter_args.items():
        attempts = attempts.filter(**{key: val})
    for key, val in exclude_args.items():
        attempts = attempts.exclude(**{key: val})

    count = attempts.count()
    end_time = 0
    start_time = 0
    suggested_end_time = end_time
    suggested_start_time = end_time

    if count > 0:
        start_time = attempts.order_by('submit_time')[0].submit_time
        end_time = attempts.order_by('-end_time')[0].end_time
        suggested_end_time = end_time
        suggested_start_time = end_time - ONE_DAY
        if suggested_start_time < start_time:
            suggested_start_time = start_time

    data = {
        'count': count,
        'end_time': end_time * 1000,
        'start_time': start_time * 1000,
        'suggested_end_time': suggested_end_time * 1000,
        'suggested_start_time': suggested_start_time * 1000,
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


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
        (filter, dot, value) = f.partition(".")
        if filter.endswith("__in"):  # multi value...
            if filter not in filter_args:
                filter_args[filter] = []
            filter_args[filter].append(value)
        else:
            filter_args[filter] = value
    return filter_args


# data.filters{name:[values]

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
    for name, value in data['filters'].iteritems():
        if name.endswith('__in'):  # list context
            values.extend(["%s.%s" % (name, val) for val in value])
        else:
            values.append("%s.%s" % (name, value))
    filter_string = "/".join(values)
    if len(filter_string) < 1:
        filter_string = "none"

    values = []
    for name, value in data['excludes'].iteritems():
        if name.endswith('__in'):  # list context
            values.extend(["%s.%s" % (name, val) for val in value])
        else:
            values.append("%s.%s" % (name, value))
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






