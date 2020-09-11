# -*- coding: utf-8 -*-
"""
ClustersBuilder splits data points in clusters by inspecting Min Spanning Tree.

Created on Fri Aug 14 10:54:34 2020

@author: Anna Kravets
"""
from clust.graphs import MST, build_edge
from clust.inspection import Inspector
import dsj_set
from functools import partial
from multiprocessing import Pool
import numpy as np
import pandas as pd

class ClustersBuilder:
    """Divides data points in clusters.

    Could build a given # of clusters or deduce optimal # of clusters
    automatically.

    Attributes
    ----------
    loader: loader.Loader
        stores data with features of data points. loader.LoaderUS should be
        used for building clusters for US counties. loader.LoaderCountries -
        for building clusters for countries.

    """

    def __init__(self, loader):
        """
        Set up Loader.

        Args:
            loader (Loader): stores data.

        Returns
        -------
          None.

        """
        self.loader = loader

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
        components = dsj_set.DisjointSets(n_vert)
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

        edge_list_tree = MST(edge_list, n_vert)
        inspector = Inspector(edge_list_tree)
        # mu=10, ratio=5 for US, mu=5, ratio=2.5 for countries
        edge_list_trunc = inspector.delete_edges_local(mu=10,
                                                       ratio_threshold=5)
        clusters = self.build_clusters_from_edge_list(edge_list_trunc, n_vert)
        clusters = sort_clusters(clusters, data,
                                 col_name=self.loader.MAIN_COLUMN)
        clusters = [set(data.iloc[i][self.loader.ID_COLUMN] for i in cluster)
                    for cluster in clusters]
        return clusters

    def save_clusters(self, date: str, file_name: str, n_clusters=5):
        """
        Build and save clusters for given date to csv file.

        Args:
            date (str): date for which clusters will be built.
            file_name (str): file to which results will be appended.
            n_clusters (int, optional): # of clusters to built. Defaults to 5.

        Returns
        -------
            None.

        """
        clusters = self.get_clusters(date)
        id_list = []
        clust_list = []
        for i in range(len(clusters)):
            for id_ in clusters[i]:
                id_list.append(id_)
                clust_list.append(i+1)
        dict_ = {'id': id_list,
                 'Cluster id': clust_list,
                 'Date': [date]*len(id_list)}
        df = pd.DataFrame.from_dict(dict_)
        df.to_csv(file_name, mode='a', header=None)


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
    edge_list = pool.map(partial(build_edge, data=data), all_pairs)
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
