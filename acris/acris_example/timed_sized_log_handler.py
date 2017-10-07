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


from acris import TimedSizedRotatingHandler
import logging
import os

record_format="[ %(asctime)s ][ %(levelname)s ][ %(message)s ][ %(module)s.%(funcName)s ]"
logdir='/tmp/logging'
os.makedirs(logdir, exist_ok=True)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create error file handler and set level to error
handler = TimedSizedRotatingHandler(os.path.join(logdir, "error.log"),"w", encoding=None, delay="true")
handler.setLevel(logging.ERROR)
formatter = logging.Formatter(record_format)
handler.setFormatter(formatter)
logger.addHandler(handler)

# create debug file handler and set level to debug
handler = TimedSizedRotatingHandler(os.path.join(logdir, "debug.log"),"w")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(record_format)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("informational message")
logger.debug("debug message")
logger.error("error message")
logger.warning("warning message")

