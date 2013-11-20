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
import base64
import re
import uuid
import datetime
import json
import time
import MySQLdb
import tempfile
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.db.models import Count
from django.db.models import Sum
from django.template import RequestContext
from django.http import Http404
from lavaFlow.models import *
log=logging.getLogger(__name__)
