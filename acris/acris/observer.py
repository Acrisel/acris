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
# Util/Observer.py
# Class support for "observer" pattern.
import acris.synchronized as sync

class Observer(object):
    def update(self, observable, arg):
        '''Called when the observed object is
        modified. You call an Observable object's
        notifyObservers method to notify all the
        object's observers of the change.'''
        pass

class Observable(sync.SynchronizeAll):
    __synchronized__=["addObserver", "deleteObserver", "deleteObservers", 
                     "setChanged", "clearChanged", "hasChanged", "countObservers"]
    def __init__(self):
        self.obs = []
        self.changed = 0
        super(Observable, self).__init__()

    def addObserver(self, observer):
        if observer not in self.obs:
            self.obs.append(observer)

    def deleteObserver(self, observer):
        self.obs.remove(observer)

    def notifyObservers(self, arg = None):
        '''If 'changed' indicates that this object
        has changed, notify all its observers, then
        call clearChanged(). Each observer has its
        update() called with two arguments: this
        observable object and the generic 'arg'.'''

        self.mutex.acquire()
        try:
            if not self.changed: return
            # Make a local copy in case of synchronous
            # additions of observers:
            localArray = self.obs[:]
            self.clearChanged()
        finally:
            self.mutex.release()
        # Updating is not required to be synchronized:
        for observer in localArray:
            observer.update(self, arg)

    def deleteObservers(self): self.obs = []
    def setChanged(self): self.changed = 1
    def clearChanged(self): self.changed = 0
    def hasChanged(self): return self.changed
    def countObservers(self): return len(self.obs)

if __name__ == '__main__':
    # Observer/ObservedFlower.py
    # Demonstration of "observer" pattern.
        
    class Flower:
        def __init__(self):
            self.isOpen = 0
            self.openNotifier = Flower.OpenNotifier(self)
            self.closeNotifier= Flower.CloseNotifier(self)
        def open(self): # Opens its petals
            self.isOpen = 1
            self.openNotifier.notifyObservers()
            self.closeNotifier.open()
        def close(self): # Closes its petals
            self.isOpen = 0
            self.closeNotifier.notifyObservers()
            self.openNotifier.close()
        def closing(self): return self.closeNotifier
    
        class OpenNotifier(Observable):
            def __init__(self, outer):
                Observable.__init__(self)
                self.outer = outer
                self.alreadyOpen = 0
                
            def notifyObservers(self):
                if self.outer.isOpen and not self.alreadyOpen:
                    self.setChanged()
                    Observable.notifyObservers(self)
                    self.alreadyOpen = 1
                    
            def close(self):
                self.alreadyOpen = 0
    
        class CloseNotifier(Observable):
            def __init__(self, outer):
                Observable.__init__(self)
                self.outer = outer
                self.alreadyClosed = 0
            def notifyObservers(self):
                if not self.outer.isOpen and not self.alreadyClosed:
                    self.setChanged()
                    Observable.notifyObservers(self)
                    self.alreadyClosed = 1
            def open(self):
                self.alreadyClosed = 0
    
    class Bee:
        def __init__(self, name):
            self.name = name
            self.openObserver = Bee.OpenObserver(self)
            self.closeObserver = Bee.CloseObserver(self)
        # An inner class for observing openings:
        class OpenObserver(Observer):
            def __init__(self, outer):
                self.outer = outer
            def update(self, observable, arg):
                print("Bee " + self.outer.name + "'s breakfast time!")
        # Another inner class for closings:
        class CloseObserver(Observer):
            def __init__(self, outer):
                self.outer = outer
            def update(self, observable, arg):
                print("Bee " + self.outer.name + "'s bed time!")
    
    class Hummingbird:
        def __init__(self, name):
            self.name = name
            self.openObserver = Hummingbird.OpenObserver(self)
            self.closeObserver = Hummingbird.CloseObserver(self)
        class OpenObserver(Observer):
            def __init__(self, outer):
                self.outer = outer
            def update(self, observable, arg):
                print("Hummingbird " + self.outer.name + "'s breakfast time!")
        class CloseObserver(Observer):
            def __init__(self, outer):
                self.outer = outer
            def update(self, observable, arg):
                print("Hummingbird " + self.outer.name + "'s bed time!")
    
    f = Flower()
    ba = Bee("Eric")
    bb = Bee("Eric 0.5")
    ha = Hummingbird("A")
    hb = Hummingbird("B")
    
    f.openNotifier.addObserver(ha.openObserver)
    f.closeNotifier.addObserver(ha.closeObserver)
    
    f.openNotifier.addObserver(hb.openObserver)
    f.closeNotifier.addObserver(hb.closeObserver)
    
    f.openNotifier.addObserver(ba.openObserver)
    f.closeNotifier.addObserver(ba.closeObserver)
    
    f.openNotifier.addObserver(bb.openObserver)
    f.closeNotifier.addObserver(bb.closeObserver)
    
    # Hummingbird 2 decides to sleep in:
    f.openNotifier.deleteObserver(hb.openObserver)
    # A change that interests observers:
    f.open()
    f.open() # It's already open, no change.
    # Bee 1 doesn't want to go to bed:
    f.closeNotifier.deleteObserver(ba.closeObserver)
    f.close()
    f.close() # It's already closed; no change
    f.openNotifier.deleteObservers()
    f.open()
    f.close()