# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 14:00:43 2020

@author: Anna Kravets
"""
from linked_list import Linked_List

class Disjoint_Sets():

  def __init__(self):
    # will store pairs: (object, set the object belongs to)
    self.mapping=dict()

  def make_set(self,x):
    """
    Creates new set that will store x and updates mapping for x.

    Args:
      x (object).

    Returns:
      None.

    """
    new_set=Linked_List()
    new_set.insert(x)
    self.mapping[x]=new_set

  def union(self, x,y):
    """
    If x and y belong to different sets, then two sets merge into one.
    The set of smaller length will be added to the set of bigger length.

    Args:
      x (object).
      y (object).

    Returns:
      None.

    """
    if self.find_set(x)==self.find_set(y):
      return
    set_to=self.mapping[x]
    set_from=self.mapping[y]

    if set_to.length<set_from.length:
      set_temp=set_to
      set_to=set_from
      set_from=set_temp

    node=set_from.head
    while node!=None:
      self.mapping[node.value]=set_to
      node=node.next_node

    set_to.append(set_from)

  def find_set(self,x):
    """
    Finds representetive of the set that x belongs to.

    Args:
      x (object): .

    Returns:
      object: representative of the set which contains x.

    """

    return self.mapping[x].head.value

