'''
Created on Dec 9, 2016

@author: arnon
'''

from acris import Mediator

def yrange(n):
    i = 0
    while i < n:
        yield i
        i += 1

n=10
m=Mediator(yrange(n))
for i in range(n):
    print(i, m.has_next(3), next(m))
print(i, m.has_next(), next(m))