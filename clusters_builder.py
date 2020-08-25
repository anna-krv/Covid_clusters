# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 10:54:34 2020

@author: Anna Kravets
"""
import graphs
import pandas as pd
import numpy as np

'''
Class represents a builder that could divide data in clusters. 
Could build a given # of clusters or deduce optimal # of clusters without any 
pregiven info. 

Attributes
----------
n_vert: int
  number of vertices (administrative units like countries or countries)
data_all_days: pandas.DataFrame
  contains statistics for all days for all admin units
name_dict: dict{int:str}
  keys are ids of admin units and values are names of admin units
country_population: pandas.DataDrame
  contains information about population of each country

'''
class Clusters_Builder:
  def __init__(self, country_info_file='data/full_grouped.csv', \
               usa_info_file='data/usa_county_wise.csv'):
    """
    Sets path to files to read data from. Reads data with statistics on all days. 

    Args:
      country_info_file (str, optional): file from which to get data about 
      all countries . Defaults to 'data/full_grouped.csv'.
      usa_info_file (str, optional): file from which to get data about US 
      counties. Defaults to 'data/usa_county_wise.csv'.

    Returns:
      None.

    """
    self.get_country_data_all_days(country_info_file)

  def get_usa_data_all_days(self, info_file):
    """
    Saves data about US counties' indicators.

    Args:
      info_file (str): name of file from which to get data about US counties.

    Returns:
      None.

    """
    self.data_all_days=pd.read_csv(info_file)
    self.data_all_days=self.data_all_days.dropna(subset=['Combined_Key'])
    self.n_vert=len(set(self.data_all_days['Combined_Key']))
    self.name_dict={i:self.data_all_days.iloc[i]['Combined_Key'] for \
                       i in range(self.n_vert)}


  def get_country_data_all_days(self, info_file):
    """
    Saves data about countries' indicators.

    Args:
      info_file (str): name of file from which to get data about countries.

    Returns:
      None.

    """
    self.data_all_days=pd.read_csv(info_file)
    self.n_vert=len(set(self.data_all_days['Country/Region']))
    self.name_dict={i:self.data_all_days.iloc[i]['Country/Region'] for \
                       i in range(self.n_vert)}
    self.country_population=pd.read_csv('data/population.csv')['Population']

  def get_clusters(self, date, n_clusters=5):
    """
    Divides countries in clusters using data on a particular date.

    Args:
      date (string): format YYYY-MM-DD for countries, MM/DD/YY for USA counties.
      n_clusters (int, optional): # of clusters to build. Defaults to 5.

    Returns:
      list: contains sets with names of admin units, each set= a distinct 
      cluster (clusters are sorted by average num of new cases in cluster, 
               ascending order).

    """
    data=self.extract_country_data(date)
    self.n_vert=data.shape[0]
    data=self.normalize_data(data)
    edge_list=self.get_edge_list(data)
    graph=graphs.Graph(self.n_vert, edge_list)
    clusters=graphs.get_clusters_optimal(graph)
    clusters=self.sort_clusters(clusters, data)
    names=[set(self.name_dict[_id] for _id in cluster) \
               for cluster in clusters]
    return names

  def sort_clusters(self, clusters, data):
    """
    Sorts clusters on avg number of new cases, ascending order.

    Args:
      clusters (list): contains sets, each set stores ids of admin units that 
      form a cluster.
      data (pandas.DataFrame): contains normalized indicators for all admin 
      units.

    Returns:
      list: contains sets(clusters), sorted.

    """
    return sorted(clusters, key=lambda cluster: self.get_rank(cluster, data))

  def get_rank(self, cluster, data):
    """
    Calculates a measure on which clusters could be sorted. 

    Args:
      cluster (set): stores ids of admin units that form a cluster.
      data (pandas.DataFrame): contains normalized indicators for all admin 
      units.

    Returns:
      float: average value of indicator 'New cases' (after it was normalized)
      for units from the given cluster.

    """
    return data.iloc[list(cluster)]['New cases'].mean()

  def extract_usa_data(self, date):
    """
    Extracts data for a particular date.

    Args:
      date (str): format MM/DD/YY for USA counties..

    Returns:
      pandas.DataFrame: contains data on given date.

    """
    data_on_date=self.data_all_days.loc[self.data_all_days['Date']==date].copy()
    column_list=['Confirmed', 'Deaths']
    data_on_date=data_on_date.loc[:,column_list]
    data_on_date=data_on_date.loc[data_on_date['Confirmed']>5]
    return data_on_date.reset_index(drop=True)

  def extract_country_data(self, date, to_scale=False):
    """
    Extracts data for a particular date.

    Args:
      date (str): format YYYY-MM-DD for countries.
      to_scale (boolean, optional): determines whether to scale indicators by
      countries' population. Defaults to False.

    Returns:
      data_on_date (pandas.DataFrame): contains data on given date.

    """
    data_on_date=self.data_all_days.loc[self.data_all_days['Date']==date].copy()
    column_list=['New cases', 'New deaths', 'New recovered']
    data_on_date=data_on_date.loc[:,column_list]
    data_on_date=data_on_date.reset_index(drop=True)
    if to_scale:
      data_on_date=self.scale_by_population(data_on_date)
    return data_on_date

  def scale_by_population(self, data):
    """
    Scales indicators by population for each country.

    Args:
      data (pandas.DataFrame): contains estimates of indicators for each country.

    Returns:
      data (pandas.DataFrame): contains estimates of indicators per 
      10 000 people for each country. 

    """
    column_list=['New cases', 'New deaths', 'New recovered']
    for name in column_list:
      data.loc[:,[name]]=data[name].values/self.country_population.values*1e4
    return data

  def normalize_data(self, data):
    """
    Performs standard normalization.

    Args:
      data (pandas.DataFrame): contains stats on a particular date.

    Returns:
      pandas.DataFrame: data after normalization.

    """
    return (data-data.mean())/(data.std())

  def edge_weight(self, data, i, j):
    """
    Calculates distance (weight of edge) between points with indexes i and j.

    Args:
      data (pandas.DataFrame): contains features of each data point.
      i (int): index of first point.
      j (int): index of another point.

    Returns:
      float: distance measured in l2 metrics.

    """
    diff=(data.iloc[i]-data.iloc[j]).values
    return np.linalg.norm(diff)

  def get_edge_list(self, data):
    """
    Gets list of weighted edges for a full graph built on given data.

    Args:
      data (pandas.DataFrame): contains features of each data point.

    Returns:
      edge_list (list): contains tuples, each stores 2 indexes and weight of 
      corresponding edge.

    """
    edge_list=[(i,j,self.edge_weight(data,i,j)) for i in range(self.n_vert)  \
               for j in range(i+1, self.n_vert)]
    return edge_list