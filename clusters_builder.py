# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 10:54:34 2020

@author: Anna Kravets
"""
import graphs
import pandas as pd
import numpy as np

'''
Divides countries in n clusters given # of new cases, new deathes,
new recovered on a particular day. Builds MST and then deletes n-1 of 
the heaviest edges.
'''
class Clusters_Builder:
  def __init__(self, country_info_file='data/full_grouped.csv', \
               usa_info_file='data/usa_county_wise.csv', n_clusters=5):
    self.get_country_data_all_days(country_info_file)
    self.n_clusters=n_clusters

  def get_usa_data_all_days(self, info_file):
    self.data_all_days=pd.read_csv(info_file)
    self.data_all_days=self.data_all_days.dropna(subset=['Combined_Key'])
    # number of administrative units
    self.n_vert=len(set(self.data_all_days['Combined_Key']))
    # keys are counties' ids, values are counties' names
    self.name_dict={i:self.data_all_days.iloc[i]['Combined_Key'] for \
                       i in range(self.n_vert)}


  def get_country_data_all_days(self, info_file):
    self.data_all_days=pd.read_csv(info_file)
    # number of administrative units
    self.n_vert=len(set(self.data_all_days['Country/Region']))
    # keys are countries' ids, values are countries' names
    self.name_dict={i:self.data_all_days.iloc[i]['Country/Region'] for \
                       i in range(self.n_vert)}
    self.country_population=pd.read_csv('data/population.csv')['Population']

  def get_clusters(self, date):
    """
    Divides countries in clusters given data on a particular date.

    Args:
      date (string): format YYYY-MM-DD for countries, MM/DD/YY for USA.

    Returns:
      list: contains clusters that have been formed.

    """
    data=self.extract_country_data(date)
    self.n_vert=data.shape[0]
    print(self.n_vert)
    data=self.normalize_data(data)
    print('normalized')
    edge_list=self.get_edge_list(data)
    print('built edge list')
    graph=graphs.Graph(self.n_vert, edge_list)
    clusters=graphs.get_clusters(graph, self.n_clusters)
    print('have clusters')
    names=[set(self.name_dict[_id] for _id in cluster) \
               for cluster in clusters]
    return names



  def extract_usa_data(self, date):
    data_on_date=self.data_all_days.loc[self.data_all_days['Date']==date].copy()
    column_list=['Confirmed', 'Deaths']
    data_on_date=data_on_date.loc[:,column_list]
    data_on_date=data_on_date.loc[data_on_date['Confirmed']>5]
    return data_on_date.reset_index(drop=True)

  def extract_country_data(self, date):
    data_on_date=self.data_all_days.loc[self.data_all_days['Date']==date].copy()
    column_list=['New cases', 'New deaths', 'New recovered']
    data_on_date=data_on_date.loc[:,column_list]
    data_on_date=data_on_date.reset_index(drop=True)
    data_on_date=self.scale_by_population(data_on_date)
    return data_on_date

  def scale_by_population(self, data):
    # data estimated per 10 000 people in a country
    column_list=['New cases', 'New deaths', 'New recovered']
    for name in column_list:
      data.loc[:,[name]]=data[name].values/self.country_population.values*1e4
    return data

  def normalize_data(self, data):
    return (data-data.mean())/(data.std())

  def edge_weight(self, data, i, j):
    diff=(data.iloc[i]-data.iloc[j]).values
    return np.linalg.norm(diff)

  def get_edge_list(self, data): #uses l2 metrics to get weight of edges
    edge_list=[(i,j,self.edge_weight(data,i,j)) for i in range(self.n_vert)  for j in range(i+1, self.n_vert)]
    return edge_list