# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 10:06:30 2020

@author: Anna Kravets
"""
import numpy as np

def build_edge(pair, data):
    """
    Calculates distance (weight of edge) between points with indexes i and j.

    Args:
      data (pandas.DataFrame): contains features of each data point.
      pair (tuple): contains 2 indexes of data points.

    Returns:
      float: distance measured in l2 metrics.

    """
    i,j=pair[0], pair[1]
    diff=(data.iloc[i]-data.iloc[j]).values
    return (i,j,np.linalg.norm(diff))