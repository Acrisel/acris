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

import time
import random
import logging
from acris import MpLogger
import os
import multiprocessing as mp

logger=logging.getLogger(__name__)

def subproc(limit=1):
    for i in range(limit):
        sleep_time=3/random.randint(1,10)
        time.sleep(sleep_time)
        logger.info("proc [%s]: %s/%s - sleep %4.4ssec" % (os.getpid(), i, limit, sleep_time))

level_formats={logging.DEBUG:"[ %(asctime)s ][ %(levelname)s ][ %(message)s ][ %(module)s.%(funcName)s(%(lineno)d) ]",
                'default':   "[ %(asctime)s ][ %(levelname)s ][ %(message)s ]",
                }
    
mplogger=MpLogger(logging_level=logging.DEBUG, level_formats=level_formats)
mplogger.start()

logger.debug("starting sub processes")
procs=list()
for limit in [1, 1]:
    proc=mp.Process(target=subproc, args=(limit, ))
    procs.append(proc)
    proc.start()
    
for proc in procs:
    if proc:
        proc.join()
    
logger.debug("sub processes completed")

mplogger.stop()