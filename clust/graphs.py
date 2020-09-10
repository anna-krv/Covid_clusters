# -*- coding: utf-8 -*-
"""
Contains function for building Minimum Spanning Tree, for building edge.
Created on Wed Aug    5 13:06:38 2020

@author: Anna Kravets
"""
import dsj_set
import numpy as np


def MST(edge_list: list, n_vert: int):
    """
    Build minimum spanning tree using Kruskal's algorithm.

    Args:
        edge_list (list): contains weighted edges in tuples.
        n_vert (int): # of vertices in graph.

    Returns
    -------
        edge_list_tree (list of Edge): contains edges that are used to build
        minimum spanning tree.

    """
    edge_list = sorted(edge_list, key=lambda edge: edge[2])
    edge_list_tree = []
    edge_index = 0
    components = dsj_set.DisjointSets(n_vert)
    while len(edge_list_tree) < n_vert-1:
        edge = edge_list[edge_index]
        from_vert, to_vert = edge[0], edge[1]
        if components.find_set(from_vert) != components.find_set(to_vert):
            components.union(from_vert, to_vert)
            edge_list_tree.append(edge)
        edge_index += 1
    return edge_list_tree


def build_edge(pair, data):
    """
    Build edge as a triple (pair[0], pair[1], weight of edge).

    Args:
      data (pandas.DataFrame): contains features of each data point.
      pair (tuple): contains 2 indexes of data points.

    Returns
    -------
      tuple: (pair[0], pair[1], distance measured in l2 metrics).

    """
    i, j = pair[0], pair[1]
    diff = (data.iloc[i]-data.iloc[j]).values
    return (i, j, np.linalg.norm(diff))
