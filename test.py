# -*- coding: utf-8 -*-
"""
Tests for disjoint_set and graphs modules.

Created on Tue Aug  4 16:18:58 2020

@author: Anna Kravets
"""
from disjoint_set import Disjoint_Sets

from disjoint_set_optimized import Disjoint_Sets as Disj_Sets_Opt

from graphs import Graph, MST

def test_general():
  disj_sets=Disjoint_Sets()
  for i in range(1,17):
    disj_sets.make_set(i)
  for i in range(1,16,2):
    disj_sets.union(i,i+1)
  for i in range(1,14,4):
    disj_sets.union(i, i+2)
  disj_sets.union(11,13)
  disj_sets.union(1,5)
  disj_sets.union(1,10)

  print(disj_sets.find_set(2))
  print(disj_sets.find_set(9))


def test_weighted_heuristic():
  disj_sets=Disjoint_Sets()
  for i in range(1,11):
    disj_sets.make_set(i)
  for i in range(1,10):
    disj_sets.union(i+1,i)
    print([disj_sets.find_set(i) for i in range(1,11)])

def test_optimized():
  ds=Disj_Sets_Opt(10)

  ds.union(2,3)
  ds.union(7,2)
  ds.union(4,2)
  ds.union(9,8)
  ds.union(0,5)
  ds.union(5,7)
  ds.union(9,1)
  ds.union(8,2)
  ds.union(3,6)
  print([ds.find_set(i) for i in range(10)])

def test_MST():
  edge_list=[]
  edge_list.append((0,1,1))
  edge_list.append((1,2,13))
  edge_list.append((2,3,15))
  edge_list.append((3,4,3))
  edge_list.append((4,5,14))
  edge_list.append((5,6,20))
  edge_list.append((6,0,17))
  edge_list.append((0,5,19))
  edge_list.append((1,6,18))
  edge_list.append((1,5,16))
  edge_list.append((1,4,2))
  edge_list.append((2,5,2))
  graph=Graph(7, edge_list)
  edge_list_tree=MST(graph)

  for edge in edge_list_tree:
    print(edge)

test_general()
print()
test_weighted_heuristic()
print()
test_optimized()
print()
test_MST()