========
LavaFlow
========

LavaFlow creates useful reports on the usage of high performance compute clusters. LavaFlow takes data from the batch scheduling system, monitoring, and other tooling, and creates reports that help administrators, managers, and end users better understand their cluster environment.  LavaFlow supports OpenLava and Grid Engine.

LavaFlow is written in Python, and uses the Django web framework. Reports are modular, new modules are easy to create using templates and Djangos query set API. LavaFlow uses human readable RESTful URLS, making it easy to automate, and share links to reports.

Charts and tables showing demand (Requested capacity) with a one-minute resolution promote data driven decisions for capacity management. Charts can be broken down by user, project, queue, job size and cluster, or rolled up to show global demand across the organization. Charts can be filtered to show only data for specific metrics, such as a project or queue. Alternatively metrics can be excluded in order to show demand for just the specific data needed.

Charts and tables showing actual utilization (Delivered capacity) with a one-minute resolution make it easy to see who used what capacity. Combined with the capacity management graphs, this provides insight into who is getting access to your HPC clusters. Graphs make it clear how much capacity was actually delivered, and makes it easy to demonstrate the effectiveness of any sharing policies in place.

The job view shows detailed information on jobs that have finished, including graphs of pending time, resource usage, and exit status for each task. Detailed information on job submission and execution information is available. Support staff and end users benefit from detailed information on the job submission and execution requirements.

Job Search makes it easy to find details about specific jobs. Both users and admins can easily interrogate the cluster for detailed information about jobs.

Job view shows detailed information on jobs that have finished, including graphs of pending time, resource usage, and exit status for each task. Detailed information on job submission and execution information.

Charts of job resource usage provide an overview of consumed resources during the jobs execution.

View tasks that ran on the same hosts at the same time. When physical resources are shared between multiple jobs, enables users and admins to find jobs that may have used more than their fair share.

See throughput per job size, spot job sizes that don’t schedule well, and understand the most common job sizes in the environment.

Use include and exclude features to show filter on any data metric to create a report with the exact data you want to see.

Quick start
-----------

1. Add "lavaFlow" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'lavaFlow',
    )

2. Include the polls URLconf in your project urls.py like this::

    url(r'^lavaFlow/', include('lavaFlow.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/polls/ to participate in the poll.
