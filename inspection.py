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
        of graph.
    """

    def __init__(self, edge_list):
        self.edge_list = edge_list

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
        if n_delete is None:
            weights = np.array([edge[2] for edge in self.edge_list])
            mean_weight = np.mean(weights)
            std_weight = np.std(weights)
            n_delete = np.sum(weights > mean_weight + std_weight)
        return self.edge_list[:-n_delete]
