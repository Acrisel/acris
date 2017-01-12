'''
Created on Jun 29, 2016

@author: arnon
'''
import pprint
import json

class Node(object):
    def __init__(self, name, value=None):
        self._name=name
        self._value=value
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, n):
        self._name = n
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, v):
        self._value = v
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __repr__(self):
        return repr(self.name) + ' : ' + repr(self.value)
    
    def __str__(self):
        return repr(self)
    
class Edge(object):
    def __init__(self, node1, node2):
        self.source=node1
        self.target=node2
        
    def from_node(self):
        return self.source
    
    def to_node(self):
        return self.target  
        
class DiGraph(object):
    def __init__(self, nodes=None):
        self.nodes= nodes if nodes else dict()
        #self.dfs_weights=dict()
        
    Node=Node
              
    def add_node(self, node):
        found=self.nodes.get(node.name)
        if not found:
            result=dict([('node', node),
                         ('nexts', list()),
                         ('prevs', list()),])
            self.nodes[node.name]=result
        return found is None          
        
    def add_edge(self, from_node, *to_nodes):
        fname=from_node.name
        fnode=self.nodes.get(fname)
        if not fnode: 
            raise Exception("EdgeError: From-Node {} not in tree".format(from_node.name))
            #fnode=self.Node(from_node)
            #self.add_node(from_node)
        
        nexts=fnode['nexts']
        for node in to_nodes:
            tname=node.name
            tnode=self.nodes.get(node.name)
            if not tnode: 
                raise Exception("EdgeError: To-Node {} not in tree".format(node.name))
            
            if tname not in nexts:
                nexts.append(tname)
            prevs=tnode['prevs']
            if fname not in prevs:
                prevs.append(fname)
            #print('Added Edge:', from_node, node)
    
    def del_edge(self, from_node, *to_nodes):
        fname=from_node.name
        fnode=self.nodes.get(fname)
        nexts=fnode['nexts']
        for node in to_nodes:
            tname=node.name
            try: nexts.remove(tname)
            except: pass
            
            tnode=self.nodes.get(tname)
            prevs=tnode['prevs']
            try: prevs.remove(fname)
            except: pass
    
    def del_node(self, node):
        dname=node.name
        dnode=self.nodes.get(dname)
        nexts=dnode['nexts']
        for tname in nexts:
            tnode=self.nodes.get(tname)
            prevs=tnode['prevs']
            try: prevs.remove(dname)
            except: pass
            
        prevs=dnode['prevs']
        for fname in prevs:
            fnode=self.nodes.get(fname)
            nexts=fnode['nexts']
            try: nexts.remove(dname)
            except: pass
        del self.nodes[dname]
    
    def _dfs(self, node_name, weights):
        props=self.nodes[node_name]
        try:
            for name in props['nexts']:
                if name not in weights.keys():
                    self._dfs(name, weights)
            weight=1+max([weights[name] for name in props['nexts']])
        except:
            weight=1
        weights[node_name]=weight
        
    def __len__(self):
        return len(self.nodes)
        
        
    def dfs(self, reverse=False):
        ''' Node iterator sorted depth first '''
        weights=dict()
        for node_name, props in self.nodes.items():
            if node_name not in weights.keys():
                self._dfs(node_name, weights)
        for name in sorted(weights.keys(), key=lambda x: weights[x], reverse=not reverse):
            yield self.nodes[name]['node']
     
    def __str__(self):
        return pprint.pformat(self.nodes) 

    def to_file(self, fp):
        json.dump(self.nodes, fp)
    
    @classmethod
    def from_file(cls, fp):
        try:
            nodes=json.load(fp)
        except:
            return None
        else:
            return cls(nodes)
 
        
if __name__ == '__main__':
    g=DiGraph()
   
    a=g.Node(('a', 1), 35)
    b=g.Node(('b', 2), 46)
    c=g.Node(('c', 3), 78)
    d=g.Node(('d', 4), 89)
    
    g.add_node(a)  
    g.add_node(b)  
    g.add_node(c)  
    g.add_node(d) 
       
    g.add_edge(a, b)
    g.add_edge(b, c)
    g.add_edge(c, d)
   
    print(g)
    
    g.del_node(d) 

    print(g)
    
    for node in g.dfs(reverse=True):
        print(node.name, node.value)
        