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
from django.conf.urls import patterns, include, url
from django.views.generic import ListView
from django.views.generic import DetailView
from lavaFlow.models import *


urlpatterns = patterns('',
                       url(r'^$', 'lavaFlow.views.utilization_view', name="lf_utilization_view_default"),
                       url(r'^get_token$', 'lavaFlow.views.get_csrf_token', name="get_token"),
                       url(r'^value_list$', 'lavaFlow.views.get_field_values', name="lf_value_list"),

                       url(
                           r'^(?P<start_time_js>\d+)/(?P<end_time_js>\d+)/exclude/(?P<exclude_string>.+?)/exclude/filter/(?P<filter_string>.+?)/filter/group/(?P<group_string>.+?)/group$',
                           'lavaFlow.views.utilization_view', name="lf_utilization_view"),
                       url(r'^clusters/$', ListView.as_view(model=Cluster, paginate_by=20), name="lf_cluster_list"),
                       url(r'^clusters/(.*?)/import/openlava$', 'lavaFlow.views.openlava_import',
                           name='lf_openlava_import'),
                       url(r'^clusters/(.*?)/import/gridengine$', 'lavaFlow.views.gridengine_import',
                           name='lf_gridengine_import'),
                       url(r'^clusters/(.*?)/import/univa82$', 'lavaFlow.views.univa82_import',
                           name='lf_univa82_import'),

                       url(r'^hosts/$', ListView.as_view(model=Host, paginate_by=20), name="lf_host_list"),
                       url(r'^users/$', ListView.as_view(model=User, paginate_by=20), name="lf_user_list"),
                       url(r'^queues/$', ListView.as_view(model=Queue, paginate_by=20), name="lf_queue_list"),
                       url(r'^projects/$', ListView.as_view(model=Project, paginate_by=20), name="lf_project_list"),
                       url(r'^attempts/$', ListView.as_view(model=Attempt, paginate_by=20), name="lf_attempt_list"),
                       url(r'^attempts/(?P<pk>\d+)$', DetailView.as_view(model=Attempt), name="lf_attempt_detail"),
                       url(r'^tasks/$', ListView.as_view(model=Task, paginate_by=20), name="lf_task_list"),
                       url(r'^tasks/(?P<pk>\d+)$', DetailView.as_view(model=Task), name="lf_task_detail"),
                       url(r'^jobs/$', ListView.as_view(model=Job, paginate_by=20), name="lf_job_list"),
                       url(r'^jobs/(?P<pk>\d+)$', DetailView.as_view(model=Job), name="lf_job_detail"),
                       url(
                           r'^cpu/(?P<start_time_js>\d+)/(?P<end_time_js>\d+)/exclude/(?P<exclude_string>.+?)/exclude/filter/(?P<filter_string>.+?)/filter/group/(?P<group_string>.+?)/group$',
                           'lavaFlow.views.cpu_consumption', name='lf_cpu_consumption_chart'),
                       url(
                           r'^submissions/(?P<start_time_js>\d+)/(?P<end_time_js>\d+)/exclude/(?P<exclude_string>.+?)/exclude/filter/(?P<filter_string>.+?)/filter/group/(?P<group_string>.+?)/group$',
                           'lavaFlow.views.submission_bar_data', name='lf_submission_chart'),
                       url(
                           r'^resource/(?P<start_time_js>\d+)/(?P<end_time_js>\d+)/exclude/(?P<exclude_string>.+?)/exclude/filter/(?P<filter_string>.+?)/filter/group/(?P<group_string>.+?)/group$',
                           'lavaFlow.views.resource_data', name='lf_resource_chart'),
                       url(
                           r'^consumption/(?P<start_time_js>\d+)/(?P<end_time_js>\d+)/exclude/(?P<exclude_string>.+?)/exclude/filter/(?P<filter_string>.+?)/filter/group/(?P<group_string>.+?)/group$',
                           'lavaFlow.views.consumption_bar_data', name='lf_consumption_chart'),
                       url(
                           r'^util_total_attempts/(?P<start_time_js>\d+)/(?P<end_time_js>\d+)/exclude/(?P<exclude_string>.+?)/exclude/filter/(?P<filter_string>.+?)/filter/group/(?P<group_string>.+?)/group$',
                           'lavaFlow.views.util_total_attempts', name='lf_util_total_attempts'),
                       url(
                           r'^util/(?P<start_time_js>\d+)/(?P<end_time_js>\d+)/exclude/(?P<exclude_string>.+?)/exclude/filter/(?P<filter_string>.+?)/filter/group/(?P<group_string>.+?)/group$',
                           'lavaFlow.views.utilization_data', name='lf_util_chart_view'),
                       url(
                           r'^utilization_table/(?P<start_time_js>\d+)/(?P<end_time_js>\d+)/exclude/(?P<exclude_string>.+?)/exclude/filter/(?P<filter_string>.+?)/filter/group/(?P<group_string>.+?)/group$',
                           'lavaFlow.views.utilization_table', name='lf_utilization_table'),

                       url(r'^util_build_filter$', 'lavaFlow.views.build_filter', name="lf_build_filter"),
)
