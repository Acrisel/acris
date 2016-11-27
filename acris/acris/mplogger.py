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
import logging
from logging.handlers import QueueListener, QueueHandler
import os
import multiprocessing as mp
from acris.timed_sized_logging_handler import TimedSizedRotatingHandler

class MpQueueListener(QueueListener):
    def __init__(self, queue, *handlers):
        super(MpQueueListener, self).__init__(queue, *handlers)
        """
        Initialise an instance with the specified queue and
        handlers.
        """
        # Changing this to a list from tuple in the parent class
        self.handlers = list(handlers)

    def handle(self, record):
        """
        Override handle a record.

        This just loops through the handlers offering them the record
        to handle.

        :param record: The record to handle.
        """
        record = self.prepare(record)
        for handler in self.handlers:
            if record.levelno >= handler.level: # This check is not in the parent class
                handler.handle(record)

    def addHandler(self, hdlr):
        """
        Add the specified handler to this logger.
        """
        if not (hdlr in self.handlers):
            self.handlers.append(hdlr)

    def removeHandler(self, hdlr):
        """
        Remove the specified handler from this logger.
        """
        if hdlr in self.handlers:
            hdlr.close()
            self.handlers.remove(hdlr)

class MpLogger(object):
    logger_initialized=False
    queue_listener=None
    
    def __init__(self, logdir=None, logging_level=logging.INFO, record_format='', logging_root=None):
        self.logdir=logdir
        self.logging_level=logging_level
        self.record_format=record_format
        self.logging_root=logging_root

    def start(self, ):
        ''' starts logger for multiprocessing using queue.
        
        logdir: if provided, error and debug logs will be created in it.
        logging_level
        logger_format
        '''
        # create console handler and set level to info
        #global logger_initialized
        #global queue_listener
        
        if MpLogger.logger_initialized:
            return
        
        if not self.record_format:
            record_format="[ %(asctime)s ][ %(levelname)s ][ %(message)s ][ %(module)s.%(funcName)s ]"
    
        MpLogger.logger_initialized=True
        logger = logging.getLogger(name=self.logging_root)
        logger.setLevel(self.logging_level)
            
        q=mp.Queue()
        queue_handler = QueueHandler(q)
        logger.addHandler(queue_handler)
        MpLogger.queue_listener = MpQueueListener(q,)
    
        handler = logging.StreamHandler()
        handler.setLevel(self.logging_level)
        formatter = logging.Formatter(record_format)
        handler.setFormatter(formatter)
        #logger.addHandler(handler)
        MpLogger.queue_listener.addHandler(handler)
    
        if self.logdir:
            # create error file handler and set level to error
            handler = TimedSizedRotatingHandler(filename=os.path.join(self.logdir, "error.log"), encoding=None, delay="true")
            handler.setLevel(logging.ERROR)
            #formatter = logging.Formatter("%(levelname)s - %(message)s")
            formatter = logging.Formatter(record_format)
            handler.setFormatter(formatter)
            #logger.addHandler(handler)
            MpLogger.queue_listener.addHandler(handler)
         
            # create debug file handler and set level to debug
            handler = TimedSizedRotatingHandler(filename=os.path.join(self.logdir, "debug.log"), )
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(record_format)
            handler.setFormatter(formatter)
            #logger.addHandler(handler)
            MpLogger.queue_listener.addHandler(handler)
            
        MpLogger.queue_listener.start()
        
    def stop(self,):
        #global queue_listener
        if MpLogger.queue_listener:
            MpLogger.queue_listener.stop()
            
    def quite(self,):
        if MpLogger.queue_listener:
            MpLogger.queue_listener.enqueue_sentinel()

 
if __name__ == '__main__':
    import time
    import random
    
    logger=logging.getLogger(__name__)
    
    def subproc(limit=1):
        for i in range(limit):
            sleep_time=3/random.randint(1,10)
            time.sleep(sleep_time)
            logger.info("proc [%s]: %s/%s - sleep %4.4ssec" % (os.getpid(), i, limit, sleep_time))
    
    mplogger=MpLogger(logging_level=logging.DEBUG)
    mplogger.start()
    
    logger.debug("starting sub processes")
    procs=list()
    for limit in [5, 5]:
        proc=mp.Process(target=subproc, args=(limit, ))
        procs.append(proc)
        proc.start()
        
    for proc in procs:
        if proc:
            proc.join()
        
    logger.debug("sub processes completed")

    mplogger.stop()