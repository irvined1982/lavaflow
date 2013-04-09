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
	url(r'^$', 'lavaFlow.views.homeView'),
	url(r'^cluster/(.+)/upload$','lavaFlow.views.uploadData'),
	url(r'^(\d+)/(\d+)/$', 'lavaFlow.views.homeView'),
	url(r'^(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.homeView'),
	
	url(r'^modules/busyUsers/(\d+)/(\d+)/(-?\w+)/$', 'lavaFlow.views.busyUsersModule'),
	url(r'^modules/busyUsers/(\d+)/(\d+)/(-?\w+)/(.*)/$', 'lavaFlow.views.busyUsersModule'),
	
	url(r'^modules/bestHosts/(\d+)/(\d+)/$', 'lavaFlow.views.bestHostModule'),
	url(r'^modules/bestHosts/(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.bestHostModule'),
	
	url(r'^modules/worstHosts/(\d+)/(\d+)/$', 'lavaFlow.views.worstHostModule'),
	url(r'^modules/worstHosts/(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.worstHostModule'),

	url(r'^modules/busySubmit/(\d+)/(\d+)/$', 'lavaFlow.views.busySubmitModule'),
	url(r'^modules/busySubmit/(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.busySubmitModule'),
	
	url(r'^modules/jobSizeChart/(\d+)/(\d+)/$', 'lavaFlow.views.jobSizeChartModule'),
	url(r'^modules/jobSizeChart/(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.jobSizeChartModule'),

	url(r'^modules/jobSizeTable/(\d+)/(\d+)/$', 'lavaFlow.views.jobSizeTableModule'),
	url(r'^modules/jobSizeTable/(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.jobSizeTableModule'),

	url(r'^modules/jobExitTable/(\d+)/(\d+)/$', 'lavaFlow.views.jobExitTableModule'),
	url(r'^modules/jobExitTable/(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.jobExitTableModule'),

	url(r'^modules/jobExitChart/(\d+)/(\d+)/$', 'lavaFlow.views.jobExitChartModule'),
	url(r'^modules/jobExitChart/(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.jobExitChartModule'),

	url(r'^modules/jobList/(\d+)/(\d+)/$', 'lavaFlow.views.jobListModule'),
	url(r'^modules/jobList/(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.jobListModule'),

	url(r'^modules/groupedUtilizationTable/(\d+)/(\d+)/group/(.*)/group/$', 'lavaFlow.views.groupedUtilizationTableModule'),
	url(r'^modules/groupedUtilizationTable/(\d+)/(\d+)/group/(.*)/group/(.*)/$', 'lavaFlow.views.groupedUtilizationTableModule'),

	url(r'^modules/groupedUtilization/(\d+)/(\d+)/group/(.*)/group/$', 'lavaFlow.views.groupedUtilizationChartModule'),
	url(r'^modules/groupedUtilization/(\d+)/(\d+)/group/(.*)/group/(.*)/$', 'lavaFlow.views.groupedUtilizationChartModule'),

	url(r'^modules/utilization/(\d+)/(\d+)/$', 'lavaFlow.views.utilizationModule'),
	url(r'^modules/utilization/(\d+)/(\d+)/(.*)/$', 'lavaFlow.views.utilizationModule'),

	url(r'^reportRange$', 'lavaFlow.views.getReportRange'),

	url(r'^jobSearch/$','lavaFlow.views.jobSearchView'), 
	url(r'^jobDetail/(\d+)/$','lavaFlow.views.jobDetailView'), 
	url(r'^runDetail/(?P<id>\d+)/$','lavaFlow.views.runDetailView'), 

	url(r'^hostView/$', 'lavaFlow.views.hostList'),
	url(r'^clusterView/$', 'lavaFlow.views.clusterList'),
	url(r'^queueView/$', 'lavaFlow.views.queueList'),
	url(r'^projectView/$', 'lavaFlow.views.projectList'),
	url(r'^userView/$', 'lavaFlow.views.userList'),
)
