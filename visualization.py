# -*- coding: utf-8 -*-
"""
Contains class that builds maps and saves images of colored clusters.

Created on Sat Aug 15 19:39:51 2020

@author: Anna Kravets
"""
import branca
import folium
import json
import loader
from datetime import datetime as dt
from datetime import timedelta
import selenium.webdriver
import requests
import pandas as pd


class MapBuilder:
    """
    Creates map, colors it in different colors based on cluster id.

    Map could be saved as html page or as an image.

    Attributes
    ----------
        geo_json:
            stores info about geography of admin units.
        clust_column:
            name of column for storing clusters' id.
        n_clust:
            number of clusters.
    """

    def __init__(self):
        """
        Load GeoJson data that will be used to draw boundaries of admin units.

        Returns
        -------
            None.

        """
        self.geo_json = self.load_geo_json()
        self.clust_column = 'Cluster id'

    def get_color(self, feature):
        """
        Get color that corresponds to cluster in which admin unit is included.

        Args:
            feature (dict): contains info about admin unit (id of admin unit is
            in feauture['properties'] dict).

        Returns
        -------
            str: color given to cluster the admin unit belongs to.

        """
        if feature['properties'][self.clust_column] == 0:
            return '#ffffff'
        return self.colorscale(feature['properties'][self.clust_column])

    def modify_geo_json(self, data):
        """
        Set new properties for GeoJson data.

        Add properties from column_list and a property 'CLuster id'.

        Args:
            data (pd.DataFrame): new properties are stored in data in
            self.column_list columns. Index column in data corresponds to
            id_json property in GeoJson.

        Returns
        -------
            None.

        """
        for i in range(len(self.geo_json['features'])):
            id_ = self.geo_json['features'][i]['properties'][self.id_json]
            for name in self.column_list + [self.clust_column]:
                self.geo_json['features'][i]['properties'][name] = 0
                if id_ in data.index.values:
                    self.geo_json['features'][i]['properties'][name] =\
                        int(data.loc[id_][name])

    def save_map_impl(self, date: str):
        """
        Create map and save it as html page.

        Args:
            date (str): is used in title of html page.

        Returns
        -------
            None.

        """
        self.colorscale = create_colorscale(self.n_clust)
        map_ = folium.Map(**self.map_args)
        folium.GeoJson(
            self.geo_json,
            style_function=lambda feature: {
                'fillColor': self.get_color(feature),
                'fillOpacity': 1,
                'color': 'black',
                'weight': 0.2
                },
            name='COVID CLUSTERS',
            tooltip=folium.features.GeoJsonTooltip(
                fields=[self.name_json]+self.column_list+[self.clust_column],
                aliases=['Name']+self.column_list+[self.clust_column])
            ).add_to(map_)
        map_.add_child(self.colorscale)

        self.add_title(map_, date)

        map_.save(self.map_folder+'/'+date+'.html')

    def save_map(self, builder, date: str):
        """
        Save map with colored clusters built for given date.

        Args:
            builder (clust.ClustersBuilder): is used to get clusters.
            date (str): for this date clusters are built.

        Returns
        -------
            None.

        """
        df = self.df[self.df['Date'] == date]
        data = builder.loader.extract_data(date)
        data = data.set_index(self.id_df)
        df = df.set_index('id')
        data[self.clust_column] = 0
        self.n_clust = len(set(df[self.clust_column].values))
        for id_ in df.index:
            data.loc[id_, self.clust_column] = df.loc[id_, self.clust_column]
        self.modify_geo_json(data)
        self.save_map_impl(date)

    def save_as_img(self, dates):
        """
        Save screenshot of webpages containing maps for particular dates.

        Args:
            dates (list): stores dates to save images for.

        Returns
        -------
            None.

        """
        driver = selenium.webdriver.Chrome()
        driver.set_window_size(1250, 800)  # 1250, 800 for US, 1100, 900 otherw
        for date in dates:
            driver.get(
                "file:///C:/Users/DELL/Covid_clusters/"+
                self.map_folder+"/"+date+".html"
                )
            driver.save_screenshot(self.img_folder+'/'+date+'.png')
            print(date)
        driver.quit()


class MapBuilderUS(MapBuilder):
    """
    Creates map of US counties, colored based on county's cluster id.

    Map could be saved as html page or as an image.

    """

    def __init__(self):
        """
        Set up specific fields for data processing, folder names, load GeoJson.

        Returns
        -------
            None.

        """
        self.id_json = 'geoid'
        self.name_json = 'namelsad'
        self.id_df = loader.LoaderUS.ID_COLUMN
        self.column_list = loader.LoaderUS.COLUMN_LIST
        self.map_folder = 'html_us'
        self.img_folder = 'pictures_us'
        self.map_args = {'location': [36, -97], 'zoomSnap': 0.25,
                         'zoom_start': 4.75, 'zoom_control': False}
        self.file_clust = 'results/usa_clust.csv'
        self.df = pd.read_csv(self.file_clust)

        MapBuilder.__init__(self)

    def load_geo_json(self):
        """
        Load counties' boundaries.

        Returns
        -------
            geo_json (dict): GeoJson data with boundaries of countries.

        """
        id_NY_list = ['36005', '36081', '36047', '36085']
        NY_id = '36061'
        path = 'data/us-county-boundaries.geojson'
        with open(path) as boundaries:
            geo_json = json.load(boundaries)
            for i in range(len(geo_json['features'])):
                id_ = geo_json['features'][i]['properties'][self.id_json]
                if id_ in id_NY_list:
                    id_ = NY_id
                geo_json['features'][i]['properties'][self.id_json] = \
                    int('840'+id_)
            return geo_json

    def add_title(self, map_: folium.Map, date: str):
        """
        Add title showing week start and end date to the map.

        Args:
            map_ (folium.Map).
            date (str): start of the following week.

        Returns
        -------
            None.

        """
        title_html = '''<head><style> html { overflow-y: hidden; }
                </style></head>
                '''
        date_prev = format(dt.strptime(date, loader.Loader.DATE_FORMAT) -
                           timedelta(days=7), '%d.%m')
        date = format(dt.strptime(date, loader.Loader.DATE_FORMAT), '%d.%m')
        title_html += '''<h1 align="center"><b>{}-{}</b></h3>'''.format(
            date_prev, date)
        map_.get_root().html.add_child(folium.Element(title_html))

class MapBuilderCountries(MapBuilder):
    """
    Creates map with countries, colored on country's cluster id.

    Map could be saved as html page or as an image.

    """

    def __init__(self):
        """
        Set up specific fields for data processing, folder names, load GeoJson.

        Returns
        -------
            None.

        """
        self.id_json = 'ADMIN'
        self.name_json = 'ADMIN'
        self.id_df = loader.LoaderCountries.ID_COLUMN
        self.column_list = loader.LoaderCountries.COLUMN_LIST
        self.img_folder = 'pictures_countries'
        self.map_folder = 'html_countries'
        self.map_args = {'tiles': "cartodbpositron", 'zoom_start': 2,
                         'location': [40., 10.], 'zoom_control': False,
                         'max_bounds': True}
        self.file_clust = 'results/countries_clust.csv'
        self.df = pd.read_csv(self.file_clust)

        MapBuilder.__init__(self)

    def load_geo_json(self):
        """
        Load countries' boundaries.

        Returns
        -------
            geo_json (dict): GeoJson data with boundaries of US counties.

        """
        country_shapes = 'https://raw.githubusercontent.com/datasets/' + \
            'geo-countries/master/data/countries.geojson'
        geo_json = json.loads(requests.get(country_shapes).text)
        name_dict = {
            'United States of America': 'US',
            'Republic of the Congo': 'Congo (Kinshasa)',
            'Democratic Republic of the Congo': 'Congo (Brazzaville)',
            'Republic of Serbia': 'Serbia',
            'Czech Republic': 'Czechia',
            'Taiwan': 'Taiwan*',
            'Macedonia': 'North Macedonia'
            }
        for i in range(len(geo_json['features'])):
            id_ = geo_json['features'][i]['properties'][self.id_json]
            if id_ in name_dict:
                geo_json['features'][i]['properties'][self.id_json] = \
                    name_dict[id_]
        return geo_json

    def add_title(self, map_: folium.Map, date: str):
        """
        Add title showing date to the map.

        Args:
            map_ (folium.Map).
            date (str).

        Returns
        -------
            None.

        """
        title_html = '''<head><style> html { overflow-y: hidden; }
                </style></head>
                '''
        title_html += '''<h1 align="center"><b>{}</b></h3>'''.format(date)
        map_.get_root().html.add_child(folium.Element(title_html))





def create_colorscale(n):
    """
    Create StepColormap for segment [0,n] with step 1.

    Colors used are yellow, orange, red.

    Args:
        n (int): segment [0,n] will be mapped to n colors.

    Returns
    -------
        colorscale (branca.colormap.StepColormap): maps segments (i,i+1] to
                                                                  diff colors.

    """
    colorscale = branca.colormap.linear.YlOrRd_09.scale(0, n)
    if n > 1:
        colorscale = colorscale.to_step(index=[i for i in range(n+1)])
    colorscale.caption = 'Cluster id'
    return colorscale
