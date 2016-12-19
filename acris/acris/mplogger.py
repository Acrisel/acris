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
from copy import copy
from acris.timed_sized_logging_handler import TimedSizedRotatingHandler
import datetime

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
            
class MicrosecondsDatetimeFormatter(logging.Formatter):
    converter=datetime.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        #print('convert:', datefmt)
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)
        return s
            
class LevelBasedFormatter(logging.Formatter):
    
    defaults={
        logging.DEBUG : "%(asctime)-15s: %(levelname)-7s: %(message)s: %(module)s.%(funcName)s(%(lineno)d)",
        'default' : "%(asctime)-15s: %(levelname)-7s: %(message)s",
        }
 
    def __init__(self, level_formats={}, datefmt=None):
        defaults=LevelBasedFormatter.defaults
        if level_formats:
            defaults=copy(LevelBasedFormatter.defaults)
            defaults.update(level_formats)
            
        self.datefmt=datefmt  
        self.defaults=dict([(level, MicrosecondsDatetimeFormatter(fmt=fmt, datefmt=self.datefmt)) for level, fmt in defaults.items()])
        self.default_format=self.defaults['default']  
        logging.Formatter.__init__(self, fmt=self.default_format, datefmt=self.datefmt)

    def format(self, record):
        formatter=self.defaults.get(record.levelno, self.default_format,)
        result = formatter.format(record)
        return result
    
def create_stream_handler(logging_level=logging.INFO, level_formats={}, datefmt=None):
    handler = logging.StreamHandler()
    handler.setLevel(logging_level)
    formatter = LevelBasedFormatter(level_formats=level_formats,datefmt=datefmt) 
    handler.setFormatter(formatter)
    return handler

class MpLogger(object):
    
    def __init__(self, logdir=None, logging_level=logging.INFO, level_formats={}, datefmt=None, logging_root=None):
        self.logdir=logdir
        self.logging_level=logging_level
        self.level_formats=level_formats
        self.datefmt=datefmt
        self.record_formatter=LevelBasedFormatter(level_formats=level_formats, datefmt=datefmt)
        self.logging_root=logging_root
        self.logger_initialized=False
        self.queue_listener=None

    def start(self, ):
        ''' starts logger for multiprocessing using queue.
        
        logdir: if provided, error and debug logs will be created in it.
        logging_level
        logger_format
        '''
        # create console handler and set level to info
        
        #if MpLogger.logger_initialized:
        if self.logger_initialized:
            return
        
        self.logger_initialized=True
        logger = logging.getLogger(name=self.logging_root)
        logger.setLevel(self.logging_level)
            
        q=mp.Queue()
        queue_handler = QueueHandler(q)
        logger.addHandler(queue_handler)
        
        self.queue_listener = MpQueueListener(q,)
        
        handler=create_stream_handler(logging_level=self.logging_level, level_formats=self.level_formats, datefmt=self.datefmt)
        #handler = logging.StreamHandler()
        #handler.setLevel(self.logging_level)
        #formatter = self.record_formatter 
        #handler.setFormatter(formatter)

        self.queue_listener.addHandler(handler)
    
        if self.logdir:
            # create error file handler and set level to error
            handler = TimedSizedRotatingHandler(filename=os.path.join(self.logdir, "error.log"), encoding=None, delay="true")
            handler.setLevel(logging.ERROR)
            formatter = self.record_formatter 
            handler.setFormatter(formatter)
            self.queue_listener.addHandler(handler)
         
            # create debug file handler and set level to debug
            handler = TimedSizedRotatingHandler(filename=os.path.join(self.logdir, "debug.log"), )
            handler.setLevel(logging.DEBUG)
            formatter = self.record_formatter 
            handler.setFormatter(formatter)

            self.queue_listener.addHandler(handler)
            
        self.queue_listener.start()
        
    def stop(self,):
        if self.queue_listener:
            self.queue_listener.stop()
            
    def quite(self,):
        if self.queue_listener:
            self.queue_listener.enqueue_sentinel()

