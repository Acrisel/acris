'''
Created on Nov 23, 2016

@author: arnon
'''
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

from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class TimedSizedRotatingHandler(TimedRotatingFileHandler, RotatingFileHandler):
    
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False, when='h', interval=1, utc=False, atTime=None):
        """ Combines RotatingFileHandler TimedRotatingFileHandler)  """
        super(TimedRotatingFileHandler, self).__init__(self, filename, when, interval, backupCount, encoding, delay, utc, atTime)
        super(RotatingFileHandler, self).__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

    def shouldRollover(self, record):
        """
        Check the need to rotate.     
        """
        timed_rollover=super(TimedRotatingFileHandler, self).shouldRollover(record) 
        sized_rollover=super(RotatingFileHandler, self).shouldRollover(record)
        
        return timed_rollover or sized_rollover

    def doRollover(self):
        """
        It is enough to use timed base rollover.
        """
        super(TimedRotatingFileHandler, self).doRollover()

    def getFilesToDelete(self):
        """
        It is enough to use timed base rollover.
        """
        return super(TimedRotatingFileHandler, self).getFilesToDelete()            