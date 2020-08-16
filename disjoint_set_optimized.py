# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 11:54:09 2020

@author: Anna Kravets
"""

'''
Mimics division of integers 0..n-1 into sets that do not intersect. 
Implements FIND SET operation on an integer and UNION operation on sets.
Uses virtual trees with path compression and union-by-rank for more
efficient operations.
'''
class Disjoint_Sets:

  def __init__(self, n):
    """
    Creates n sets, each set contains one integer i where i in [0..n-1].

    Args:
      n (int): number of elements.

    Returns:
      None.

    """
    # stores index of parent for each element.
    self.parents=[i for i in range(n)]
    # stores ranks of elements - upper bound on number of children of
    # the element.
    self.ranks=[0]*n
    # is true and sensible only for roots of trees
    self.tree_size=[1]*n

  def union(self, id1, id2):
    """
    Merges two sets: one containing int id1 and one containing id2, if
    they are distinct. Updates ranks.

    Args:
      id1 (int): one of ints.
      id2 (int): one of ints.

    Returns:
      None.

    """
    parent1=self.find_set(id1)
    parent2=self.find_set(id2)
    if parent1==parent2:
      return

    new_parent=parent2 if self.ranks[parent2]>=self.ranks[parent1] else parent1
    old_parent=parent1 if self.ranks[parent2]>=self.ranks[parent1] else parent2

    self.parents[old_parent]=new_parent

    if self.ranks[new_parent]==self.ranks[old_parent]:
      self.ranks[new_parent]+=1

    self.tree_size[new_parent]+=self.tree_size[old_parent]


  def find_set(self,i):
    """
    Returns representative id of the set to which the element i belongs. 
    Implements path compression.

    Args:
      i (int): element for which the set is being looked up.

    Returns:
      int: representative id of the set containing ith element.

    """
    parent=self.parents[i]
    if self.parents[parent]!=parent:
      self.parents[i]=self.find_set(parent)
    return self.parents[i]

  def get_all_sets(self):
    """
    Generates list of sets of elements.

    Returns:
      all_sets (list): contains sets that have been formed.

    """
    all_sets=dict()
    for i in range(len(self.parents)):
      parent=self.find_set(i)
      if parent in all_sets:
        all_sets[parent].add(i)
      else:
        all_sets[parent]={i}
    return list(all_sets.values())