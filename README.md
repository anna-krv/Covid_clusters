# Covid_clusters
 The goal of this project is to build clusters on base of MST (minimum spanning tree) of a graph. First, MST is built, then its edges are inspected. Edges that are globally (or locally) inconsistent are deleted. Components that are left are treated as separate clusters.
 
This approach was applied to analyze COVID-19 statistics (in period of 22/01/20 - 27/07/20). USA counties were split in clusters on # of confirmed cases and deaths per a week period. Countries were split in clusters on # of new cases, new deaths, new recovered each day. Results were animated to show daily changes for countries and weekly changes for USA counties.   
