# -*- coding: utf-8 -*-
"""
Contains class that builds maps and creates pictures of geo clusters.

Created on Sat Aug 15 19:39:51 2020

@author: Anna Kravets
"""
import branca
import folium
import json
import loader
import selenium.webdriver
import requests

class MapBuilder:
    def __init__(self):
        self.geo_json = self.load_geo_json()

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
        id_ = feature['properties'][self.id_json]
        if id_ not in self.df_dict:
            return '#ffffff'
        return self.colorscale(self.df_dict[id_])

    def modify_geo_json(self, data):
        for i in range(len(self.geo_json['features'])):
            id_ = self.geo_json['features'][i]['properties'][self.id_json]
            for name in self.col_names + ['Cluster id']:
                self.geo_json['features'][i]['properties'][name] = 0
            for name in self.col_names:
                if id_ in data[self.id_df].values:
                    self.geo_json['features'][i]['properties'][name] =\
                        int(data[data[self.id_df] == id_][name].values[0])
            if id_ in self.df_dict:
                self.geo_json['features'][i]['properties']['Cluster id'] = \
                    self.df_dict[id_]

    def create_map(self, n, date):
        self.colorscale = create_colorscale(n)
        m = folium.Map(**self.map_args)
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
                fields=[self.name_json]+self.col_names+['Cluster id'],
                aliases=['Name']+self.col_names+['Cluster id'])
            ).add_to(m)
        m.add_child(self.colorscale)

        title_html = '''<head><style> html { overflow-y: hidden; }
            </style></head>
            '''
        title_html += '''<h1 align="center"><b>{}</b></h3>'''.format(date)
        m.get_root().html.add_child(folium.Element(title_html))

        m.save(self.map_folder+'/'+date+'.html')

    def save_map(self, builder, date):
        clusters = builder.get_clusters(date)
        data = builder.loader.extract_data(date)
        n_clust = len(clusters)
        self.df_dict = {id_: i+1 for i in range(n_clust) for id_ in clusters[i]}
        self.modify_geo_json(data)
        self.create_map(n_clust, date)

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
        driver.set_window_size(1100, 900) # 1800, 800 for US
        for date in dates:
            driver.get(
                "file:///C:/Users/DELL/Covid_clusters/"+self.map_folder+"/"+date+".html"
                )
            driver.save_screenshot(self.img_folder+'/'+date+'.png')
            print(date)
        driver.quit()


class MapBuilderUS(MapBuilder):
    def __init__(self):
        self.id_json = 'geoid'
        self.name_json = 'namelsad'
        self.id_df = loader.LoaderUS.ID_COLUMN
        self.col_names = loader.LoaderUS.COLUMN_LIST
        self.map_folder = 'html_us'
        self.img_folder = 'pictures_us'
        self.map_args = {'location': [36, -97], 'zoomSnap': 0.25,
                         'zoom_start': 4.75, 'zoom_control': False}

        MapBuilder.__init__(self)

    def load_geo_json(self):
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

class MapBuilderCountries(MapBuilder):
    def __init__(self):
        self.id_json = 'ADMIN'
        self.name_json = 'ADMIN'
        self.id_df = loader.LoaderCountries.ID_COLUMN
        self.col_names = loader.LoaderCountries.COLUMN_LIST
        self.img_folder = 'pictures_countries'
        self.map_folder = 'html_countries'
        self.map_args = {'tiles': "cartodbpositron", 'zoom_start': 2,
                         'location': [40., 10.], 'zoom_control': False,
                         'max_bounds': True}

        MapBuilder.__init__(self)

    def load_geo_json(self):
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
