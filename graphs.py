# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 13:06:38 2020

@author: Anna Kravets
"""
from disjoint_set_optimized import Disjoint_Sets
import numpy as np

class Graph:
  def __init__(self, n_vert:int, edge_list:list):
    """
    Creates an undirected graph with vertices numbered 0..n_vert-1,
    and weighted edges.

    Args:
      n_vert (int): number of vertices.
      edge_list (list): contains triples (from_vert, to_vert, weigth).

    Returns:
      None.

    """
    self.n_vert=n_vert
    self.edge_list=[Edge(triple[0], triple[1], triple[2]) for triple \
                    in edge_list]


class Edge:
  def __init__(self, from_vert, to_vert, weight):
    self.from_vert=from_vert
    self.to_vert=to_vert
    self.weight=weight
  def __str__(self):
    return 'from: '+str(self.from_vert)+' to: '+str(self.to_vert)\
      +' weight: '+str(self.weight)


def get_clusters(graph:Graph, n_clusters:int):
  """
  Builds n_clusters on vertices from graph. Uses procedure for building MST but
  stops when gets n_clusters # of connected components.

  Args:
    graph (Graph): connected, undirected graph with weighted edges.
    n_clusters (int): number of clusters to build.

  Returns:
    list: contains sets that have been formed, set=cluster.

  """
  edge_list=sorted(graph.edge_list, key=lambda edge: edge.weight)
  edge_list_tree=[]
  edge_index=0
  components=Disjoint_Sets(graph.n_vert)
  optimal_size=graph.n_vert/n_clusters
  while len(edge_list_tree)<graph.n_vert-n_clusters:
    edge=edge_list[edge_index]
    from_vert, to_vert=edge.from_vert, edge.to_vert
    parent_from=components.find_set(from_vert)
    parent_to=components.find_set(to_vert)
    if parent_from!=parent_to and \
      components.tree_size[parent_from]<180 and \
        components.tree_size[parent_to]<180:
      components.union(from_vert, to_vert)
      edge_list_tree.append(edge)
    edge_index+=1
  return components.get_all_sets()


def get_clusters_optimal(graph:Graph):
  """
  Builds optimal # of clusters on vertices from graph. Uses procedure for building 
  MST and then deletes edges with weight W>Mean_weight+std_weight.

  Args:
    graph (Graph): connected, undirected graph with weighted edges.

  Returns:
    list: contains sets that have been formed, set=cluster.

  """
  edge_list=sorted(graph.edge_list, key=lambda edge: edge.weight)
  edge_list_tree=[]
  edge_index=0
  components=Disjoint_Sets(graph.n_vert)
  components_history=[components.get_all_sets()]
  while len(edge_list_tree)<graph.n_vert-1:
    edge=edge_list[edge_index]
    from_vert, to_vert=edge.from_vert, edge.to_vert
    parent_from=components.find_set(from_vert)
    parent_to=components.find_set(to_vert)
    if parent_from!=parent_to:
      components.union(from_vert, to_vert)
      components_history.append(components.get_all_sets())
      edge_list_tree.append(edge)
    edge_index+=1
  weights=np.array([edge.weight for edge in edge_list_tree])
  mean_weight=np.mean(weights)
  std_weight=np.std(weights)
  num_edge_to_delete=np.sum(weights>mean_weight+std_weight)
  return components_history[-num_edge_to_delete-1]

def MST(graph: Graph):
  """
  Builds minimum spanning tree using Kruskal's algorithm.

  Args:
    graph (Graph): connected, undirected graph with weighted edges.

  Returns:
    edge_list_tree (list of Edge): contains edges that are used to build 
    minimum spanning tree.

  """
  edge_list=sorted(graph.edge_list, key=lambda edge: edge.weight)
  edge_list_tree=[]
  edge_index=0
  components=Disjoint_Sets(graph.n_vert)
  while len(edge_list_tree)<graph.n_vert-1:
    edge=edge_list[edge_index]
    from_vert, to_vert=edge.from_vert, edge.to_vert
    if components.find_set(from_vert)!=components.find_set(to_vert):
      components.union(from_vert, to_vert)
      edge_list_tree.append(edge)
    edge_index+=1
  return edge_list_tree