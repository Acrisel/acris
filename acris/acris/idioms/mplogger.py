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
from .timed_sized_logging_handler import TimedSizedRotatingHandler
from datetime import datetime
import sys   

class MpQueueListener(QueueListener):
    def __init__(self, queue, *handlers, name='mplogger', logging_level=logging.INFO, logdir=None, formatter=None, process_key=[], force_global=False):
        super(MpQueueListener, self).__init__(queue, *handlers)
        """ Initialize an instance with the specified queue and
        handlers.
        
        Args:
            handlers: list of handlers to apply
            process_key: list of keys by which to bind handler to records.
                handlers that don't have any key are classified as global handlers.
                if record doens't have any matching key, global handlers will be used.
                if records match, only matching handlers will be used. 
        """
        self.process_key=process_key
        self.logdir=logdir
        self.formatter=formatter
        self.force_global=force_global
        self.name=name
        
        key_handlers=dict([(p, dict()) for p in process_key])
                    
        self.key_handlers=key_handlers
        self.global_handlers=list(handlers)
        self.console_handlers=list()
        self.logging_level=logging_level
        
    def handle(self, record):
        """ Override handle a record.

        This just loops through the handlers offering them the record
        to handle.

        Args:
            record: The record to handle.
        """
        
        # Find handlers that match process keys
        handlers=list()
        for process_key in self.process_key:
            record_key=record.__dict__.get(process_key, None)
            if record_key: 
                process_handlers=self.key_handlers[process_key]
                key_handlers=process_handlers.get(record_key, None)
                if not key_handlers:
                    name="%s.%s" % (self.name, record_key)
                    key_handlers=get_file_handlers(logging_level=self.logging_level, logdir=self.logdir, process_key=name, formatter=self.formatter)
                    process_handlers[record_key]=key_handlers
                handlers.extend(key_handlers)
                
        if self.force_global or len(handlers) == 0:
            handlers.extend(self.global_handlers)
            
        if len(self.console_handlers) > 0:
            handlers.extend(self.console_handlers)
        
        record = self.prepare(record)
        for handler in list(set(handlers)):
            if record.levelno >= handler.level: # This check is not in the parent class
                handler.handle(record)

    def addConsoleHandler(self, handler):
        self.console_handlers.append(handler)
        
    def addHandler(self, handler):
        """
        Add the specified handler to this logger.
        
        handler is expected to have process_key attribute.
        process_key attribute is expected to be a list of records attribute names that handler would bind to.
        if handler does not have process_key attribute or it is empty, handler will be associated with 
        """
        key_bind=False
        if hasattr(handler, 'process_key'):
            handler_key=handler.process_key
            for key in list(set(self.process_key) & set(handler_key)):
                exist_handler=self.key_handlers.get(key, list())
                self.key_handlers[key]=exist_handler
                exist_handler.append(handler)
                key_bind=True
        if not key_bind:
            self.global_handlers.append(handler)

    def removeHandler(self, hdlr):
        """
        Remove the specified handler from this logger.
        """
        if hdlr in self.handlers:
            hdlr.close()
            self.handlers.remove(hdlr)
            
class MicrosecondsDatetimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        
        if ct is  None:
            ct=datetime.now()
            
        if datefmt is not None:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)
            
        return s
            
class LevelBasedFormatter(logging.Formatter):
    
    defaults={
        logging.DEBUG : u"%(asctime)-15s: %(process)-7s: %(levelname)-7s: %(message)s: %(module)s.%(funcName)s(%(lineno)d)",
        'default' : u"%(asctime)-15s: %(process)-7s: %(levelname)-7s: %(message)s",
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
    handlers=list()
    
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging_level)
    formatter = LevelBasedFormatter(level_formats=level_formats,datefmt=datefmt) 
    stdout_handler.setFormatter(formatter)
    handlers.append(stdout_handler)
    
    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    
    return handlers

def get_file_handlers(logdir='', logging_level=logging.INFO, process_key=None, formatter=None):
    result=list()
    
    #key_s=''
    if process_key: name="%s.log" % process_key
    else: name='mplogger.log'
    
    #name="error%s.log" % key_s
    handler = TimedSizedRotatingHandler(filename=os.path.join(logdir, name), encoding=None, delay="true")
    handler.setLevel(logging_level)
    handler.setFormatter(formatter)
    result.append(handler)
    # create error file handler and set level to error
    '''
    name="error%s.log" % key_s
    handler = TimedSizedRotatingHandler(filename=os.path.join(logdir, name), encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    handler.setFormatter(formatter)
    result.append(handler)

    # create debug file handler and set level to debug
    name="debug%s.log" % key_s
    handler = TimedSizedRotatingHandler(filename=os.path.join(logdir, name), )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    result.append(handler)
    '''
    return result

class MpLogger(object):
    ''' Builds Multiprocessing logger such all process share the same logging mechanism 
    '''
    def __init__(self, name='mplogger', logdir=None, logging_level=logging.INFO, level_formats={}, datefmt=None, process_key=[], console=True, force_global=False, logging_root=None, handlers=[]):
        '''Initiates MpLogger service
        
        Args:
            name: base name to use for file logs.
            logdir: folder to which log files will be written; if not provided, log files will not be created
            logging_level: level from which logging will be done 
            level_formats: mapping of logging levels to formats to use for constructing message
            datefmt: date format to use
            process_key: list of record names that would be used to create files
            force_global: when set, records assigned to process_key handler will also routed to global handlers.
            logging_root: ???
            handlers: list of global handlers 
        '''
        
        self.logdir=logdir
        self.logging_level=logging_level
        self.level_formats=level_formats
        self.datefmt=datefmt
        self.record_formatter=LevelBasedFormatter(level_formats=level_formats, datefmt=datefmt)
        self.logging_root=logging_root
        self.logger_initialized=False
        self.queue_listener=None
        self.handlers=handlers
        self.process_key=process_key
        self.force_global=force_global
        self.console=console
        self.name=name
        
    def add_file_handlers(self, process_key=''):
        #if pid in self.pids: return
        #pid_s=''
        #if pid: pid_s=".%s" % pid
        if not process_key: process_key=self.name
        global_handlers=get_file_handlers(logdir=self.logdir, logging_level=self.logging_level, process_key=process_key, formatter=self.record_formatter)
        for handler in global_handlers:
            self.queue_listener.addHandler(handler)        

    def start(self, ):
        ''' starts logger for multiprocessing using queue.
        
        logdir: if provided, error and debug logs will be created in it.
        logging_level: logging level from which to report
        logger_format: formating per logging level
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
        
        self.queue_listener = MpQueueListener(q, name=self.name, logging_level=self.logging_level, logdir=self.logdir, formatter=self.record_formatter, process_key=self.process_key, force_global=self.force_global)
    
        if len(self.handlers) == 0:
            if self.console:
                handlers=create_stream_handler(logging_level=self.logging_level, level_formats=self.level_formats, datefmt=self.datefmt)            
                for handler in handlers:
                    self.queue_listener.addConsoleHandler(handler)
            
            if self.logdir and self.force_global:
                self.add_file_handlers(process_key=self.name)
            
        else: # len(self.handlers) > 0:
            for handler in self.handlers:
                self.queue_listener.addHandler(handler)
            
        self.queue_listener.start()
        
    def stop(self,):
        if self.queue_listener:
            self.queue_listener.stop()
            
    def quite(self,):
        if self.queue_listener:
            self.queue_listener.enqueue_sentinel()

