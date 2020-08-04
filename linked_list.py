# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 14:57:40 2020

@author: Anna Kravets
"""
class Linked_List():
  def __init__(self):
    self.head=None
    self.tail=None
    self.length=0

  def insert(self, x):
    if self.head==None:
      self.head=Node(x)
      self.tail=self.head
    else:
      self.tail.next_node=Node(x)
      self.tail=self.tail.next_node
    self.length+=1

  def append(self, other):
    if other.length==0:
      return

    if self.head==None:
      self.head=other.head
    else:
      self.tail.next_node=other.head

    self.tail=other.tail
    self.length+=other.length

class Node():
  def __init__(self, x, next_node=None):
    self.value=x
    self.next_node=next_node