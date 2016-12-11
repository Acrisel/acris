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

from acris.singleton import Singleton
from acris.sequence import Sequence
from acris.data_types import MergedChainedDict
import threading
from abc import abstractmethod
from collections import OrderedDict
#from acris.synchronized.sav.1 import SynchronizeAll, dont_synchronize, Synchronization, synchronized
from acris.decorated_class import decorated_class, traced_method
from acris.threaded import threaded

#traced=traced_method(None, True)


resource_id=Sequence('ResourcePool_Resource')

class ResourcePoolError(Exception):
    pass

class Resource(object):

    def __init__(self, *args, **kwargs):
        '''Instantiate Resource to used in Resource Pool
        
        Args:
            name: resource name
        '''
        self.args=args
        self.kwargs=kwargs
        #self.resource_id=resource_id()
        self.resource_name=self.__class__.__name__
        
    def __repr__(self):
        result="Resource(name:%s)" % (self.resource_name, )#self.resource_id)
        return result 
    
    @abstractmethod
    def activate(self):
        ''' activates resource
        
        Returns:
            activated resource
        '''
        return self
    
    @abstractmethod
    def deactivate(self):
        ''' deactivates resource
        
        Returns:
            deactivated resource
        '''
        return self
        
    @abstractmethod
    def active(self):
        ''' test if resource is active
        '''
        return True
    
        
class ResourcePool(Singleton): 
    ''' Singleton pool to managing resources of multiple types.
    
    ResourcePool uses Singleton characteristics to maintain pool per resource name.
    
    Pool policy:
        If there is resource in the pool: provide
        If there is no resource in the pool:
            if limitless, manufacture new by provided resourceFactory
            if limited:
                if nowait: return empty
                if wait with no time limit: wait until resource is available.
                if wait with time limit: halt wait and return with resource if available or empty
                if callback, reserve resource and notify availability with reference to reserved resource
                
    Policy can only be set one immediately after initialization.
    
    '''
    
    __policy = {'autoload': True, # automatically load resources when fall behind
                'load_size': 1, # when autoload, number of resources to load
                'resource_limit': -1, # max resources available
                'activate_on_load': False, # when loading, if set, activate resource
                'activate_on_get': False, # when get, activate resource if not already active
                'deactivate_on_put': False, # when returning resource, deactivate, if set.
        }
    
    __allow_set_policy=True
    __lock=threading.Lock()
    
    __name=''
    
    __ticket_sequence=Sequence('ResourcePool')
    
    #@traced
    def __init__(self, resource_cls=Resource, policy={}):
        # sets resource pool policy overriding defaults
        
        self.__resource_cls=resource_cls
        self.__available_resources=list()
        self.__awaiting=OrderedDict()
        self.__reserved=OrderedDict()
        self.__inuse_resources=list()
        self.mutex = threading.RLock()
        #self.__ticket_sequence=Sequence("ResourcePool.%s" % (resource_cls.__name__, ))
        
        if self.__allow_set_policy:
            self.__policy=MergedChainedDict(policy, self.__policy)
        else:
            self.__lock.release()
            raise ResourcePoolError("ResourcePool already in use, cannot set_policy")
    
    def __repr__(self):
        return "ResourcePool( class: %s, policy: %s)" %(self.__resource_cls.__name__, self.__policy)
    
    def __load(self, sync=False, count=-1):
        ''' loads resources into pool
        '''
        if sync: self.__lock.acquire()
        self.__allow_set_policy=False
        if count < 0:
            load_size=self.__policy['load_size']
            resource_limit=self.__policy['resource_limit']
            count=min(load_size, resource_limit) if resource_limit >=0 else load_size
        
        count=count-len(self.__available_resources) 
        if count > 0: 
            activate_on_load=self.__policy['activate_on_load']
            for _ in range(count):
                resource=self.__resource_cls()
                try:
                    if activate_on_load: resource.activate()
                except Exception as e:
                    raise e
                self.__available_resources.append(resource)  
        if sync: self.__lock.release()          
    
    def load(self, count=-1):
        ''' loads resources into pool
        '''
        self.__load(sync=True, count=-1)         
        return self
    
    def __remove_ticket(self, ticket):
        #self.__lock.acquire()
        del self.__reserved[ticket]
        #self.__lock.release()
    
    
    @threaded
    def __wait_on_condition_callback(self, condition, seconds, ticket, callback):
        try:
            with condition:
                condition.wait(seconds)
        except RuntimeError:
            pass
        except Exception as e:
            raise e
        
           
        callback(ticket)
        
    def __wait_on_condition_here(self, condition, seconds, ticket):
        try:
            with condition:
                condition.wait(seconds)
        except RuntimeError:
            pass
        except Exception as e:
            raise e
        
        # process finished waiting either due to time passed
        # or that resources were reserved.  
        # Hence, try to pick reserved resources
        result=self.__reserved.get(ticket, None)
        if result: 
            self.__remove_ticket(ticket)

        return result
        
        
    def __wait(self, sync, count, wait, callback=None):
        ''' waits for count resources, 
        
        wait uses condition object.  put method would use 
        the same condition object to notify wait of resources 
        reserved for this request.
        
        It is assumed that calling process is separated thread.  
        Otherwise, process deadlocks.
        
        Args:
            sync: (boolean) work in object synchronized, if set
            count: number of resources to wait on
            callback: callable to call back once resources are available
            
        Returns:
            list of resources, if callback is not provided (None)
            reservation ticked to use once called back, if callback is provided.
        
        '''
        seconds=None if wait <0 else wait
        condition = threading.Condition()
        ticket=self.__ticket_sequence()
        self.__awaiting[ticket]=(condition, count,)
        
        if sync: self.__lock.release()
        
        if not callback:
            result=self.__wait_on_condition_here(condition, seconds, ticket)
        else:
            self.__wait_on_condition_callback(condition, seconds, ticket, callback)
            result=None
         
        return result

    def _get(self, sync=False, count=1, wait=-1, callback=None, hold_time=None, ticket=None):
        self.__allow_set_policy=False
        
        if ticket is not None:
            # process finished waiting either due to time passed
            # or that resources were reserved.  
            # Hence, try to pick reserved resources
            result=self.__reserved.get(ticket, None)
            if result: 
                self.__remove_ticket(ticket)
                return result
             
        
        resource_limit=self.__policy['resource_limit']
        if resource_limit > -1 and count >resource_limit:
            raise ResourcePoolError("Trying to get count (%s) larger than resource limit (%s)" % (count, resource_limit))
        
        if sync: self.__lock.acquire()
        
        activate_on_get=self.__policy['activate_on_get']
        # If there are awaiting processes, wait too, and this call is not after
        # put (for an awated process).
        if len(self.__awaiting) > 0 and sync:
            resources=self.__wait(sync=sync, count=count, wait=wait, callback=callback)
            if activate_on_get: self.__activate_allocated_resource(resources)
            return resources
        
        # try to see if request can be addressed by existing or by loading new 
        # resources.
        available_loaded=len(self.__available_resources)
        inuse_resources=len(self.__inuse_resources)
        hot_resources=available_loaded+inuse_resources
        missing_to_serve=count-available_loaded
        if missing_to_serve < 0: missing_to_serve=0
        allowed_to_load=resource_limit-hot_resources if resource_limit > 0 else missing_to_serve
        
        to_load=min(missing_to_serve, allowed_to_load)
        
        #print("TOLOAD: %s (available_loaded: %s, missing_to_serve: %s, allowed_to_load: %s, inuse_resources %s, hot_resources: %s)" % \
        #      (to_load, available_loaded, missing_to_serve, allowed_to_load, inuse_resources, hot_resources))
        if to_load > 0:
            self.__load(sync=False, count=to_load)
            
        # if resources are available to serve the request, do so.
        # if not, and there is wait, then do wait.
        # otherwise return no resources.
        if len(self.__available_resources) >= count:
            # There are enough resources to serve!
            resources=self.__available_resources[:count]
            self.__available_resources=self.__available_resources[count:]
            self.__inuse_resources.extend(resources)
            if sync: self.__lock.release()
        elif wait != 0:
            # No resources.  But need to wait.
            resources=self.__wait(sync=sync, count=count, wait=wait, callback=callback)
        else:
            # No resources and no need to wait; we are done!
            resources=[]
            if sync: self.__lock.release()
            pass
        
        if activate_on_get: self.__activate_allocated_resource(resources)
        return resources
    
    def get(self, count=1, wait=-1, callback=None, hold_time=None, ticket=None):
        ''' retrieve resource from pool
        
        get checks for availability of count resources. If available: provide.
        If not available, and no wait, return empty
        If wait, wait for a seconds.  If wait < 0, wait until available.
        If about to return empty and callback is provided, register reserved with hold_time.
        When reserved, callback will be initiated with reservation_ticket.  The receiver, must call
        get(reservation_ticket=reservation_ticket) again to collect reserved resources.
        
        Important, when using wait, it is assumed that calling process is separated thread.  
        Otherwise, process deadlocks.

        Warnings: 
            1. if count > resource_limit, call will be rejected.  
            2. if count > 1 and resources are limited due to high activity or 
                clients not putting back resources, caller may be in deadlock.
            
        Args:
            count: number of resource to grab 
            wait: number of seconds to wait if none available. 
                0: don't wait
                negative: wait until available
                positive: wait period
            callback: notify that resources are available to collect
            hold_time: seconds to hold reserve resources on callback.  
                If not collected in within the specify period, reserved go
                back to pull.
            ticket: reserved ticket provided in callback to allow client pick their 
                reserved resources. 
            
        Raises:
            ResourcePoolError
        '''
        
        # some validation:
        if callback and not callable(callback):
            raise ResourcePoolError("Callback must be callable, but it is no: %s" % repr(callback))
        
        result=self._get(sync=True, count=count, wait=wait, callback=callback, hold_time=hold_time, ticket=ticket)
        return result

    
    def __activate_allocated_resource(self, resources):
        for resource in resources:
            try:
                if not resource.active: resource.activate()
            except Exception as e:
                raise e
                   
    def put(self, *resource):
        ''' adds resource to this pool
        
        Args:
            resource: Resource object to be added to pool
        '''
        
        # validate that all resources provided are legal
        self.__lock.acquire()
        pool_resource_name=self.__resource_cls.__name__
        
        for rsc in resource: 
            resource_name=rsc.__class__.__name__
            if pool_resource_name != resource_name:
                raise ResourcePoolError("ResourcePool resource class (%s) doesn't match returned resource (%s)" % \
                                        (pool_resource_name, resource_name))
        
        # deposit resource back to available
        resources=list(resource)
        deactivate_on_put=self.__policy['deactivate_on_put']
        if deactivate_on_put:
            for resource in resources: 
                try:
                    resource.deactivate()
                except Exception as e:
                    raise e
            
        self.__available_resources.extend( list(resource) )
        self.__inuse_resources=self.__inuse_resources[:len(resources)]
        
        for ticket, (condition, count) in list(self.__awaiting.items()):
            if count <= len(self.__available_resources):
                self.__reserved[ticket]=self._get(count=count)
                with condition:
                    #print("Notifying awaiting.")
                    condition.notify()
                del self.__awaiting[ticket]
            else:
                # this is an interesting scenario.
                # e.g., first awaiting for 3 resources. But there is only one available.
                #       second awaits for 1 resources.  If we serve it, first will have 
                #       to wait longer.  If we don't, first is holding the line.
                #       Predictive module will learn if it is better to hold the line,
                #       
                break
        self.__lock.release()      

    