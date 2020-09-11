# -*- coding: utf-8 -*-
"""
Class that deletes inconsistent edges from Minimum Spanning Tree of graph.

Created on Sat Sep  5 12:17:47 2020

@author: Anna Kravets
"""
import numpy as np


class Inspector:
    """Deletes inconsistent edges and builds clusters on remaining graph.

    Attributes
    ----------
        edge_list (list): contains edges from MST(minimum spanning tree)
        of graph. Edges are sorted in ascending order based on weights.
    """

    def __init__(self, edge_list):
        self.edge_list = edge_list
        self.n_vert = len(edge_list)+1

    def delete_edges(self, n_delete=None):
        """
        Delete edges that are inconsistent (globally).

        Edge's inconsistency is based on how its weight compares to
        others' weights).

        Args:
            n_delete (int, optional): # of edges to delete, if not given will
                be deduced automatically. Defaults to None.

        Returns
        -------
            list: edges that remain after deletion of inconsistent ones.

        """
        if n_delete == 0:
            return self.edge_list
        if n_delete is None:
            weights = np.array([edge[2] for edge in self.edge_list])
            mean_weight = np.mean(weights)
            std_weight = np.std(weights)
            n_delete = np.sum(weights > mean_weight + std_weight)
        return self.edge_list[:-n_delete]

    def delete_edges_local(self, mu=10, ratio_threshold=5):
        self.edge_dict = self.get_dict()
        new_edge_list = []
        for edge in self.edge_list:
            if is_consistent(self.edge_dict, edge, mu, ratio_threshold):
                new_edge_list.append(edge)
        return new_edge_list

    def get_dict(self):
        edge_dict = [[] for i in range(self.n_vert)]
        for edge in self.edge_list:
            for vert in [edge[0], edge[1]]:
                edge_dict[vert].append(edge)
        return edge_dict


def is_consistent(edge_dict, edge_to_check, mu, ratio_threshold):
    from_vert, to_vert = edge_to_check[0], edge_to_check[1]
    weight_to_check = edge_to_check[2]
    is_consistent = True

    for vert in [from_vert, to_vert]:
        another_vert = from_vert+to_vert-vert
        vert_list, weight_list = get_neighbours(vert, another_vert, edge_dict)
        for neighbour in vert_list:
            new_vert_list, new_weight_list = get_neighbours(neighbour,
                                                            vert, edge_dict)
            weight_list += new_weight_list
        if len(weight_list) > 0:
            avg = np.mean(weight_list)
            std = np.std(weight_list)
            ratio = weight_to_check/avg if avg > 0 else 1
            if weight_to_check > avg+mu*std and ratio > ratio_threshold:
                is_consistent = False
    return is_consistent

def get_neighbours(vert, vert_to_avoid, edge_dict):
    vert_list = []
    weight_list = []
    for edge in edge_dict[vert]:
        neighbour = edge[0]+edge[1]-vert
        if neighbour != vert_to_avoid:
            vert_list.append(neighbour)
            weight_list.append(edge[2])
    return vert_list, weight_list
