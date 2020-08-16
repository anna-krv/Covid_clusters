# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 14:00:43 2020

@author: Anna Kravets
"""

class Disjoint_Sets:
  def __init__(self):
    # stores pairs (object, index of object in parents list)
    self.mapping=dict()
    # stores index of parent for object with corresponding index
    self.parents=[]
    # stores ranks of objects with corresponding index
    self.ranks=[]

  def make_set(self,x):
    """
    If x has not been already seen, then it creates new id for x and 
    saves its parent and rank.

    Args:
      x (object): new element on which the new set will be created.

    Returns:
      None.

    """
    if not x in self.mapping:
      new_id=len(self.parents)
      self.mapping[x]=new_id
      self.parents.append(new_id)
      self.ranks.append(0)

  def union(self, x, y):
    """
    Merges two sets: one containing object x and one containing y, if
    they are distinct. Updates ranks.

    Args:
      x (object): one of objects.
      y (object): one of objects.

    Returns:
      None.

    """
    self.union_impl(self.mapping[x],self.mapping[y])

  def union_impl(self, id1, id2):
    """
    Merges two sets: one containing object with id1 and one containing
    object with id2, if they are distinct. Updates ranks.

    Args:
      id1 (int): one of indexes.
      id2 (int): one of indexes.

    Returns:
      None.

    """
    parent1=self.find_set_impl(id1)
    parent2=self.find_set_impl(id2)
    if parent1==parent2:
      return

    new_parent=parent2 if self.ranks[parent2]>=self.ranks[parent1] else parent1
    old_parent=parent1 if self.ranks[parent2]>=self.ranks[parent1] else parent2

    self.parents[old_parent]=new_parent

    if self.ranks[new_parent]==self.ranks[old_parent]:
      self.ranks[new_parent]+=1

  def find_set(self,x):
    """
    Returns representative id of the set to which object belongs. 
    Implements path compression.

    Args:
      x (object): object for which the set is being looked up.

    Returns:
      int: representative id of the set containing object with given 
      index.

    """
    return self.find_set_impl(self.mapping[x])

  def find_set_impl(self,index):
    """
    Returns representative id of the set to which object with 
    corresponding index belongs. Implements path compression.

    Args:
      index (int): id of object for which the set is being looked up.

    Returns:
      int: representative id of the set containing object with given 
      index.

    """
    parent=self.parents[index]
    if self.parents[parent]!=parent:
      self.parents[index]=self.find_set_impl(parent)
    return self.parents[index]