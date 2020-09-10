# -*- coding: utf-8 -*-
"""
Demonstates how to build clusters and save result as picture.

Created on Tue Aug  4 13:46:34 2020

@author: Anna Kravets
"""
import clust
import loader
import visualization

if __name__ == '__main__':
    cluster_builder = clust.ClustersBuilder(loader.LoaderCountries())
    dates = ['15.04.20']
    map_builder = visualization.MapBuilderCountries()
    for date in dates:
        map_builder.save_map(cluster_builder, date)
    map_builder.save_as_img(dates)
