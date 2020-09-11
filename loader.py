# -*- coding: utf-8 -*-
"""
Loader stores data in a data frame and extracts data relevant to given date.

Created on Sat Sep  5 09:57:37 2020

@author: Anna Kravets
"""
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd


class Loader:
    """Stores data from specified files. Extracts data relevent to given date.

    Attributes
    ----------
        DATE_FORMAT (str): format in which dates sould be passed to methods.

    """

    DATE_FORMAT = '%d.%m.%y'

    def __init__(self):
        self.data_all_days = pd.read_csv(self.INFO_FILE)
        self.n_vert = len(set(self.data_all_days[self.ID_COLUMN]))

    def extract_data(self, date):
        """
        Extract data for a particular date.

        Args:
            date (str): format as in DATE_FORMAT.

        Returns
        -------
            pandas.DataFrame: contains data on given date.

        """
        date = format(dt.strptime(date, self.DATE_FORMAT).date(),
                      self.DATE_FORMAT_INTERNAL)
        data_on_date = \
            self.data_all_days.loc[self.data_all_days['Date'] == date].copy()
        column_list = self.COLUMN_LIST + [self.ID_COLUMN]
        data_on_date = data_on_date.loc[:, column_list]
        return data_on_date.reset_index(drop=True)


class LoaderCountries(Loader):
    """Stores data from specified files. Extracts data relevent to given date.

    Attributes
    ----------
        DATE_FORMAT_INTERNAL (str): format in which dates are stored
        in INFO_FILE.
        INFO_FILE (str): file with data about all countries.
        POPULATION_INFO_FILE (str): file with data on population of countries
        present in COUNTRY_INFO_FILE.
        ID_COLUMN (str): name of column with a unique value for each country.
        COLUMN_LIST (list): contains names of columns that are used in
        analysis.
        MAIN_COLUMN (str): name of column. On values from this column clusters
        will be sort.

    """

    DATE_FORMAT_INTERNAL = '%Y-%m-%d'
    INFO_FILE = 'data/full_grouped.csv'
    POPULATION_INFO_FILE = 'data/population.csv'
    ID_COLUMN = 'Country/Region'
    COLUMN_LIST = ['New cases', 'New deaths', 'New recovered']
    MAIN_COLUMN = 'New cases'

    def __init__(self):
        """
        Save data about countries' indicators on all dates.

        Returns
        -------
            None.

        """
        Loader.__init__(self)
        self.country_population = \
            pd.read_csv(self.POPULATION_INFO_FILE)['Population']

    def extract_data(self, date, to_scale=False):
        """
        Extract data for a particular date.

        Args:
            date (str): format as in DATE_FORMAT.
            to_scale (boolean, optional): determines whether to scale
            indicators by countries' population. Defaults to False.

        Returns
        -------
            data_on_date (pandas.DataFrame): contains data on given date.

        """
        data_on_date = Loader.extract_data(self, date)
        if to_scale:
            data_on_date = self.scale_by_population(data_on_date)
        return data_on_date

    def scale_by_population(self, data):
        """
        Scale indicators by population for each country.

        Args:
            data (pandas.DataFrame): contains estimates of indicators for each
            country.

        Returns
        -------
            data (pandas.DataFrame): contains estimates of indicators per
            10 000 people for each country.

        """
        column_list = ['New cases', 'New deaths', 'New recovered']
        for name in column_list:
            data.loc[:, [name]] = data[name].values / \
                self.country_population.values*1e4
        return data


class LoaderUS(Loader):
    """Stores data from specified files. Extracts data relevent to given date.

    Attributes
    ----------
        DATE_FORMAT_INTERNAL (str): format in which dates are stored in
        INFO_FILE.
        INFO_FILE (str): file from which to get data about US counties.
        ID_COLUMN (str): name of column with a unique value for each country.
        COLUMN_LIST (list): contains names of columns that are used in
        analysis.
        MAIN_COLUMN (str): name of column. On values from this column clusters
        will be sort.

    """

    DATE_FORMAT_INTERNAL = '%#m/%#d/%y'
    INFO_FILE = 'data/usa_county_wise.csv'
    ID_COLUMN = 'UID'
    COLUMN_LIST = ['Confirmed', 'Deaths']
    MAIN_COLUMN = 'Confirmed'

    def extract_data(self, date):
        """
        Extract data for a particular date.

        Args:
            date (str): format as in DATE_FORMAT.

        Returns
        -------
            pandas.DataFrame: contains data on given date.

        """
        data_on_date = Loader.extract_data(self, date)
        date_on_prev_week = format(dt.strptime(date, Loader.DATE_FORMAT) -
                                   timedelta(days=7), Loader.DATE_FORMAT)
        data_on_prev_week = Loader.extract_data(self, date_on_prev_week)
        data = data_on_date
        data['Confirmed'] = data['Confirmed'] - data_on_prev_week['Confirmed']
        data['Deaths'] = data['Deaths'] - data_on_prev_week['Deaths']
        data = data.loc[data['Confirmed'] + data['Deaths'] > 0]
        return data.reset_index(drop=True)
