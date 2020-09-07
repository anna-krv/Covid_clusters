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


class ClustersBuilder:
    """Rrepresents a builder that could divide data points in clusters.

    Could build a given # of clusters or deduce optimal # of clusters without any
    pregiven info.

    Attributes
    ----------
    loader:
        stores data with features of vertices.

    """

    def __init__(self):
        """
        Set up Loader.

        Returns
        -------
          None.

        """
        self.loader = None

    def build_clusters_from_edge_list(self, edge_list, n_vert):
        """
        Build clusters as joint components of graph built on given edge_list.

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
        data = self.loader.extract_data(date)
        n_vert = data.shape[0]
        data_norm = normalize_data(data.loc[:, self.loader.COLUMN_LIST])
        edge_list = get_edge_list(data_norm)

        edge_list_tree = graphs.MST(edge_list, n_vert)
        inspector = inspection.Inspector(edge_list_tree)
        # mu=20, ratio=8 for US
        edge_list_trunc = inspector.delete_edges_local(mu=5,
                                                       ratio_threshold=2.5)
        clusters = self.build_clusters_from_edge_list(edge_list_trunc, n_vert)
        clusters = sort_clusters(clusters, data,
                                 col_name=self.loader.MAIN_COLUMN)
        clusters = [set(data.iloc[i][self.loader.ID_COLUMN] for i in cluster)
                 for cluster in clusters]
        return clusters

class ClustersBuilderUS(ClustersBuilder):
    def __init__(self):
        """
        Set up Loader.

        Returns
        -------
          None.

        """
        self.loader = loader.LoaderUS()

class ClustersBuilderCountries(ClustersBuilder):
    def __init__(self):
        """
        Set up Loader.

        Returns
        -------
          None.

        """
        self.loader = loader.LoaderCountries()


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
