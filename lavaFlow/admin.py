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
# $Rev: 261 $:
# $Author: ubuntu $:
# $Date: 2013-01-21 22:49:34 +0100 (Mon, 21 Jan 2013) $:
#
# Create your views here.
from django.contrib import admin
from lavaFlow.models import *
for i in [ImportKey, OpenLavaSubmitOption, OpenLavaTransferFileOption, JobStatus, Cluster, Project, Host, Queue, Job, OpenLavaTransferFile, OpenLavaResourceLimit, JobSubmitOpenLava, Task, Attempt, AttemptResourceUsage, OpenLavaExitInfo]:
	admin.site.register(i)
