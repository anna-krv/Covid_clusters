# -*- coding: utf-8 -*-
"""
Demonstates how to build clusters and save result as picture.

Created on Tue Aug  4 13:46:34 2020

@author: Anna Kravets
"""
import clust
import loader
import visualization
import time

dates = ['09.03.20']

if __name__ == '__main__':
    cluster_builder = clust.ClustersBuilder(loader.LoaderUS())
    map_builder = visualization.MapBuilderUS()

    for date in dates:
        print(date)
        start = time.time()
        cluster_builder.save_clusters(date, 'us_clust.csv')
        print('time elapsed: ', time.time()-start)
        map_builder.save_map(cluster_builder,date)
    map_builder.save_as_img(dates)