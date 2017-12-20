# -*- encoding: utf-8 -*-
##############################################################################
#
#    Acrisel LTD
#    Copyright (C) 2008- Acrisel (acrisel.com) . All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from .VERSION import __version__

from acrilib import traced_method, LogCaller
from acrilib import Threaded, RetriveAsycValue, threaded
from acrilib import Singleton, NamedSingleton, Sequence
from acrilib import TimedSizedRotatingHandler, MergedChainedDict
import acris.idioms.resource_pool as resource_pool
import acris.idioms.virtual_resource_pool as virtual_resource_pool
import acris.idioms.virtual_resource_pool_db as virtual_resource_pool_db
from .idioms.resource_pool import ResourcePool, Resource, Requestor, Requestors
from acrilib import Synchronization, SynchronizeAll, dont_synchronize, do_synchronize, synchronized
from acrilib import Mediator
from acris.misc.msort  import msort
from acris.osutils.mail import send_mail