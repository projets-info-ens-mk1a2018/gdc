#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gdc.py
#  
#  Copyright 2018 Arthur Luciani <arthur@arthur-X550JD>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from urllib.parse import unquote

keyword = "train"


class Node:
    def __init__(self, obj=None, parent=None):
        self.parent = parent
        self.children = []
        self.obj = obj
        self.level = 0
        
    def getSiblings(self):
        if self.parent:
            return self.parent.children.remove(self)
        else :
            return []
    
    def getParent(self):
        return self.parent
    
    def getChildren(self):
        return self.children[:]
    
    def newChild(self, obj=None):
        c = Node(obj, self)
        self.children.append(c)
        c.level = self.level + 1
        return c
    
    def getValue(self):
        return self.obj
    
    def getNode(self, obj):
        if self.obj == obj:
            return self
        for c in self.everyChild():
            if c.obj == obj:
                return c
        raise KeyError("Object not in this tree")
    
    def everyChild(self):
        l = []
        if self.children:
            l.extend(self.children[:])
            for c in self.children:
                l.extend(c.everyChild())
        return l
    
    def removeChild(self, child):
        if child in self.children:
            for gc in child.children:
                child.removeChild(gc)
            self.children.remove(child)
        else :
            raise IndexError("Not one of its children")
    
    def dict(self):
        if self.children:
            return {N : N.dict() for N in self.children}
        else:
            return obj
    
    def _rprint(self, indent):
        p_list = ["\n{}|--".format("   "*indent), self.obj]
        for c in self.children:
            p_list.extend(c._rprint(indent+1))
        return p_list
    
    def print(self, indent=0):
        print(self.obj, end='')
        p_list = []
        for c in self.children:
            p_list.extend(c._rprint(indent))
        
        for o in p_list:
            print(o, end='')
        print('\n')
    
    def __iter__(self):
        it = [self.obj]
        for c in self.children:
            it.extend(c)
        for e in it:
            yield e

def newTree():
    return Node("root")

def nodeDistance(node_a, node_b):
    d = 0
    level = node_a
    try :
        while node_b.obj not in level:
            d += 1
            level = level.parent
        level = node_b
        while node_a.obj not in level:
            d += 1
            level = level.parent
        return d
    except AttributeError:
        return 10000

def urldecode(s):
    return unquote(s)


def themes(keyword):
    portails = dict()
    for url in search('site:fr.wikipedia.org {}'.format(keyword), stop=5):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for link in soup.find_all('a'):
            l = urldecode(str(link.get('href')))
            if "/wiki/Portail:" in l:
                l = l[14:].split('/')[0]
                if l == "Accueil":
                    continue
                try :
                    portails[l] += 1
                except KeyError:
                    portails[l] = 1
    return portails
 
# on récupère l'arborescence des portails
r = requests.get("http://fr.wikipedia.org/wiki/Portail:Accueil")
soup = BeautifulSoup(r.text, 'html.parser')

portail = newTree()    
les_h = soup.find_all(["h{}".format(i) for i in range(2, 7)])

tag_level = 1
node = portail
for h_tag in les_h:
    if int(h_tag.name[1]) > tag_level:
        node = node.newChild(h_tag)
        tag_level += 1
    elif int(h_tag.name[1]) == tag_level:
        node = node.parent.newChild(h_tag)
    else :
        while int(h_tag.name[1]) < tag_level:
            node = node.parent
            tag_level -= 1
        node = node.parent.newChild(h_tag)


top_level = [node for node in portail.everyChild() if not node.children]
h_tags = list(portail)
for node in portail.everyChild():
    tag = node.obj.next_sibling
    next_node = False
    while tag and tag not in h_tags and not next_node:
        try:
            for link in tag.find_all('a'):
                l = urldecode(str(link.get('href')))
                if "/wiki/Portail:" in l:
                    l = l[14:].split('/')[0]
                    node.newChild(l)
                    next_node = True
        except:
            pass
        tag = tag.next_sibling


for c in portail.everyChild():
    if type(c.obj) != str:
        for span in c.obj.find_all('span'):
            try:
                name = span['id']
            except:
                pass
        c.obj = name

for i in range(2):
    for c in portail.children:
        if c.obj == "Conseils":
            portail.removeChild(c)

#portail.print()
top_level = [node for node in portail.everyChild() if not node.children]
print(len(list(portail)))



if __name__ == '__main__' :
    portails = themes(keyword)
    portails = sorted(portails, key=lambda x:-portails[x])
    for p in portails:
        node_a = portail.getNode(p)
        d = sum([nodeDistance(node_a, portail.getNode(port)) for port in portails])
        print(p, d)


