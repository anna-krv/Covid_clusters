# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 16:18:58 2020

@author: Anna Kravets
"""
from disjoint_set_with_list import Disjoint_Sets

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
  for i in range(1,17):
    disj_sets.make_set(i)
  for i in range(1,16):
    disj_sets.union(i+1,i)
    print([disj_sets.find_set(i) for i in range(1,17)])



test_general()

test_weighted_heuristic()