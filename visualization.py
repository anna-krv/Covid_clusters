# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 19:39:51 2020

@author: Anna Kravets
"""
import clusters_builder
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster
import numpy as np
import pandas as pd
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2




n=100


def get_continent(col):
    try:
        cn_a2_code =  country_name_to_country_alpha2(col)
    except:
        cn_a2_code = 'Unknown' 
    try:
        cn_continent = country_alpha2_to_continent_code(cn_a2_code)
    except:
        cn_continent = 'Unknown' 
    return (cn_a2_code, cn_continent)


geolocator = Nominatim(user_agent="anna_visualization_for_covid")
def geolocate(country):
    try:
        # Geolocate the center of the country
        loc = geolocator.geocode(country)
        # And return latitude and longitude
        return (loc.latitude, loc.longitude)
    except:
        # Return missing value
        return np.nan


clusters_dict={0:['Ukraine',0], 1:['Poland',1], 2:['Russia',2], 3:['China',3], \
               4:['USA',4]}

df=pd.DataFrame.from_dict(clusters_dict,orient='index', columns=['CountryName', 'Cluster'])

df['codes']=df['CountryName'].apply(get_continent)
df['Country']=df['codes'].apply(lambda pair: pair[0])
df['Continent']=df['codes'].apply(lambda pair: pair[1])

df['Geolocate']=df['Country'].apply(geolocate)
df['latitude']=df['Geolocate'].apply(lambda pair: pair[0])
df['longitude']=df['Geolocate'].apply(lambda pair: pair[1])


print(df)

#empty map
world_map= folium.Map(tiles="cartodbpositron")
marker_cluster = MarkerCluster().add_to(world_map)
#for each coordinate, create circlemarker of user percent
for i in range(len(df)):
        #lat = df.iloc[i]['Geolocate'][0]
        #long = df.iloc[i]['Geolocate'][1]
        radius=8
        popup_text = """Country : {}<br>
                    %of Cluster : {}<br>"""
        popup_text = popup_text.format(df.iloc[i]['Country'],
                                   df.iloc[i]['Cluster']
                                   )
        folium.CircleMarker(location = list(df.iloc[i]['Geolocate']), radius=radius, popup= popup_text, fill =True).add_to(marker_cluster)
#show the map
world_map.save('my_map.html')


#Setting up the world countries data URL
url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'


country_shapes = f'{url}/world-countries.json'
m= folium.Map(tiles="cartodbpositron")
folium.Choropleth(
    #The GeoJSON data to represent the world country
    geo_data=country_shapes,
    name='choropleth COVID-19',
    data=df,
    #The column aceppting list with 2 value; The country name and  the numerical value
    columns=['CountryName', 'Cluster'],
    key_on='feature.properties.name',
    fill_color='PuRd',
    nan_fill_color='white'
).add_to(m)
m.save('covid.html')