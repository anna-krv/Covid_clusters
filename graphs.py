# -*- coding: utf-8 -*-
"""
Created on Wed Aug    5 13:06:38 2020

@author: Anna Kravets
"""
from disjoint_set_optimized import Disjoint_Sets

class Graph:
    def __init__(self, n_vert: int, edge_list: list):
        """
        Create an undirected graph with vertices numbered 0..n_vert-1,
        and weighted edges.

        Args:
            n_vert (int): number of vertices.
            edge_list (list): contains triples (from_vert, to_vert, weigth).

        Returns
        -------
            None.

        """
        self.n_vert = n_vert
        self.edge_list = [Edge(triple[0], triple[1], triple[2]) for triple \
                                        in edge_list]


class Edge:
    def __init__(self, from_vert, to_vert, weight):
        self.from_vert = from_vert
        self.to_vert = to_vert
        self.weight = weight

    def __str__(self):
        return 'from: '+str(self.from_vert)+' to: '+str(self.to_vert)\
            + ' weight: '+str(self.weight)


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
    components = Disjoint_Sets(n_vert)
    while len(edge_list_tree) < n_vert-1:
        edge = edge_list[edge_index]
        from_vert, to_vert = edge[0], edge[1]
        if components.find_set(from_vert) != components.find_set(to_vert):
            components.union(from_vert, to_vert)
            edge_list_tree.append(edge)
        edge_index += 1
    return edge_list_tree
