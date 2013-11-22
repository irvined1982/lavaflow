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
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView
from django.views.generic import DetailView
from lavaFlow.models import * 

urlpatterns = patterns('',
		url(r'^hosts/$', ListView.as_view(model=Host, paginate_by=20), name="host_list" ),
		url(r'^users/$', ListView.as_view(model=User, paginate_by=20), name="user_list" ),
		url(r'^queues/$', ListView.as_view(model=Queue, paginate_by=20), name="queue_list" ),
		url(r'^cluster/(.*?)/import/openlava$', 'lavaFlow.views.openlava_import', name='openlava_import'),
		url(r'^attempts/$', ListView.as_view(model=Attempt, paginate_by=20), name="attempt_list" ),
		url(r'^attempts/(?P<pk>\d+)$', DetailView.as_view(model=Attempt), name="attempt_detail"),
		url(r'^tasks/$', ListView.as_view(model=Task, paginate_by=20), name="task_list" ),
		url(r'^tasks/(?P<pk>\d+)$', DetailView.as_view(model=Task), name="task_detail"),
		url(r'^jobs/$', ListView.as_view(model=Job, paginate_by=20), name="job_list" ),
		url(r'^jobs/(?P<pk>\d+)$', DetailView.as_view(model=Job), name="job_detail"),
		url(r'^util/(?P<starttime>\d+)/(?P<endtime>\d+)/filter/(?P<filter_string>.+?)/filter/group/(?P<group_string>.+?)/group$', 'lavaFlow.views.utilization_data', name='util_view_both'),
		url(r'^util/(?P<starttime>\d+)/(?P<endtime>\d+)/filter/filter/group/(?P<group_string>.+?)/group$', 'lavaFlow.views.utilization_data', name='util_view_group'),
		url(r'^util/(?P<starttime>\d+)/(?P<endtime>\d+)/filter/filter/group/group$', 'lavaFlow.views.utilization_data', name='util_view_none'),
		url(r'^util/(?P<starttime>\d+)/(?P<endtime>\d+)/filter/(?P<filter_string>.+?)/filter/group/group$', 'lavaFlow.views.utilization_data', name='util_view_filter'),
		)
