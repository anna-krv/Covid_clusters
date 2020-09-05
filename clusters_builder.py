# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 10:54:34 2020

@author: Anna Kravets
"""
from disjoint_set_optimized import Disjoint_Sets
import edges
from functools import partial
import graphs
import inspection
import loader
from multiprocessing import Pool
import numpy as np
import pandas as pd


class Clusters_Builder:
    """Rrepresents a builder that could divide data points in clusters.

    Could build a given # of clusters or deduce optimal # of clusters without any
    pregiven info.

    Attributes
    ----------
    n_vert: int
        number of vertices (administrative units like countries or countries)
    loader: loader.Loader
        stores data with features of vertices.

    """

    def __init__(self):
        """
        Set up Loader.

        Returns
        -------
          None.

        """
        self.loader = loader.Loader()

    def get_n_clusters(self, graph: graphs.Graph, n_clusters: int):
        """
        Build n_clusters on vertices from graph.

        Uses procedure for building MST but stops when gets n_clusters # of
        connected components.

        Args:
            graph (Graph): connected, undirected graph with weighted edges.
            n_clusters (int): number of clusters to build.

        Returns
        -------
            list: contains sets that have been formed, set=cluster.

        """
        edge_list = sorted(graph.edge_list, key=lambda edge: edge.weight)
        edge_list_tree = []
        edge_index = 0
        components = Disjoint_Sets(graph.n_vert)
        optimal_size = graph.n_vert/n_clusters
        while len(edge_list_tree)<graph.n_vert-n_clusters:
            edge = edge_list[edge_index]
            from_vert, to_vert = edge.from_vert, edge.to_vert
            parent_from = components.find_set(from_vert)
            parent_to = components.find_set(to_vert)
            if parent_from != parent_to and \
                components.tree_size[parent_from] < 180 and \
                    components.tree_size[parent_to] < 180:
                components.union(from_vert, to_vert)
                edge_list_tree.append(edge)
            edge_index += 1
        return components.get_all_sets()


    def get_clusters_optimal(self, edge_list, n_vert):
        """
        Build optimal # of clusters on vertices from graph. Use procedure for
        building MST and then delete edges with weight W>Mean_weight+std_weight.

        Args:
            edge_list (list): list with triples of weighted edges:
                (from vert, to vert, weight).
            n_vert (int): number of vertices.

        Returns
        -------
            list: contains sets that have been formed, set=cluster.

        """
        edge_list = sorted(edge_list, key=lambda edge: edge[2])
        edge_list_tree = []
        edge_index = 0
        components = Disjoint_Sets(n_vert)
        components_history = [components.get_all_sets()]
        while len(edge_list_tree) < n_vert-1:
            edge = edge_list[edge_index]
            from_vert, to_vert = edge[0], edge[1]
            parent_from = components.find_set(from_vert)
            parent_to = components.find_set(to_vert)
            if parent_from != parent_to:
                components.union(from_vert, to_vert)
                components_history.append(components.get_all_sets())
                edge_list_tree.append(edge)
            edge_index += 1

        weights = np.array([edge[2] for edge in edge_list_tree])

        mean_weight = np.mean(weights)
        std_weight = np.std(weights)
        num_edge_to_delete = np.sum(weights > mean_weight + std_weight)
        return components_history[-num_edge_to_delete-1], weights

    def build_clusters_from_edge_list(self, edge_list, n_vert):
        """
        Build clusters as joint components of graph built on edge_list.

        Args:
            edge_list (list): list with triples of weighted edges:
                (from vert, to vert, weight).
            n_vert (int): number of vertices.

        Returns
        -------
            list: contains sets that have been formed, set=cluster.

        """
        components = Disjoint_Sets(n_vert)
        for edge in edge_list:
            from_vert, to_vert = edge[0], edge[1]
            components.union(from_vert, to_vert)
        return components.get_all_sets()

    def get_clusters(self, date, n_clusters=5):
        """
        Divide admin units in clusters using data on a particular date.

        Args:
        ----
            date (string): format as in DATE_FORMAT.
            n_clusters (int, optional): # of clusters to build. Defaults to 5.

        Return
        ------
            list: contains sets with names of admin units, each set =  a
            distinct cluster (clusters are sorted by average num of new cases
                              in cluster, ascending order).

        """
        data = self.loader.extract_usa_data(date)
        n_vert = data.shape[0]
        print(n_vert)
        data_norm = normalize_data(data.loc[:, ['Confirmed', 'Deaths']])
        edge_list = get_edge_list(data_norm)
        print('edges')
        edge_list_tree = graphs.MST(edge_list, n_vert)
        weights = np.array([edge[2] for edge in edge_list_tree])
        print('MST')
        inspector = inspection.Inspector(edge_list_tree)
        edge_list_trunc = inspector.delete_edges()
        clusters = self.build_clusters_from_edge_list(edge_list_trunc, n_vert)
        print('clust')
        clusters = sort_clusters(clusters, data, col_name='Confirmed')
        names = [set((data.iloc[_id]['UID'],
                      self.loader.get_name(data.iloc[_id]['UID']))
                     for _id in cluster) for cluster in clusters]
        return weights, names


def get_edge_list(data):
    """
    Get list of weighted edges for a full graph built on given data.

    Args:
        data (pandas.DataFrame): contains features of each data point.

    Returns
    -------
        edge_list (list): contains tuples, each stores 2 indexes and weight
        of corresponding edge.

    """
    n_vert = data.shape[0]
    all_pairs = np.array([(i, j) for i in range(n_vert)
                          for j in range(i+1, n_vert)])
    pool = Pool(4)
    edge_list = pool.map(partial(edges.build_edge, data=data), all_pairs)
    pool.close()
    pool.join()
    return edge_list


def normalize_data(data):
    """
    Perform standard normalization.

    Args:
        data (pandas.DataFrame): contains stats on a particular date.

    Returns
    -------
        pandas.DataFrame: data after normalization.

    """
    return (data-data.mean())/(data.std())


def sort_clusters(clusters, data, col_name='New cases'):
    """
    Sort clusters on avg number of new cases, ascending order.

    Args:
        clusters (list): contains sets, each set stores ids of admin units that
        form a cluster.
        data (pandas.DataFrame): contains normalized indicators for all admin
        units.
        col_name (str): name of column, to take data for calculating rank.
        Defaults to 'New cases' (for countries sort).

    Returns
    -------
        list: contains sets(clusters), sorted.

    """
    return sorted(clusters, key=lambda cluster: get_rank(cluster,
                                                         data, col_name))


def get_rank(cluster, data, col_name):
    """
    Calculate a measure on which clusters could be sorted.

    Args:
        cluster (set): stores ids of admin units that form a cluster.
        data (pandas.DataFrame): contains normalized indicators for all admin
        units.
        col_name (str): name of column, to take data for calculating rank.

    Returns
    -------
        float: average value of indicator giben by col_name (after
        it was normalized)
        for units from the given cluster.

    """
    return data.iloc[list(cluster)][col_name].mean()
