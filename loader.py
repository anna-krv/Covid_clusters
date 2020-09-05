# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 09:57:37 2020

@author: Anna Kravets
"""
from datetime import datetime as dt
import pandas as pd


class Loader:
    """Stores data from specified files. Extracts data relevent to given date.

    Attributes
    ----------
        DATE_FORMAT (str): format in which dates sould be passed to the
        class' methods.
        COUNTRY_DATE_FORMAT (str): format in which dates are stored
        in COUNTRY_INFO_FILE.
        US_DATE_FORMAT (str): format in which dates are stored in USA_INFO_FILE.
        COUNTRY_INFO_FILE (str): file with data about all countries.
        POPULATION_INFO_FILE (str): file with data on population of countries
        present in COUNTRY_INFO_FILE.
        USA_INFO_FILE (str): file from which to get data about US counties.

    """

    DATE_FORMAT = '%d.%m.%y'
    COUNTRY_DATE_FORMAT = '%Y-%m-%d'
    US_DATE_FORMAT = '%#m/%#d/%y'
    COUNTRY_INFO_FILE = 'data/full_grouped.csv'
    POPULATION_INFO_FILE = 'data/population.csv'
    USA_INFO_FILE = 'data/usa_county_wise.csv'

    def __init__(self):
        """
        Read data with statistics on all days.

        Returns
        -------
            None.

        """
        self.get_usa_data_all_days()

    def get_usa_data_all_days(self):
        """
        Save data about US counties' indicators.

        Returns
        -------
            None.

        """
        self.data_all_days = pd.read_csv(Loader.USA_INFO_FILE)
        self.data_all_days = self.data_all_days.dropna(subset=['Combined_Key'])
        self.n_vert = len(set(self.data_all_days['Combined_Key']))
        self.name_dict = {
            self.data_all_days.iloc[i]['UID']:
                self.data_all_days.iloc[i]['Combined_Key'] for
                i in range(self.n_vert)}

    def get_country_data_all_days(self):
        """
        Save data about countries' indicators.

        Returns
        -------
            None.

        """
        self.data_all_days = pd.read_csv(Loader.COUNTRY_INFO_FILE)
        self.n_vert = len(set(self.data_all_days['Country/Region']))
        self.name_dict = {i: self.data_all_days.iloc[i]['Country/Region'] for
                          i in range(self.n_vert)}
        self.country_population = \
            pd.read_csv(Loader.POPULATION_INFO_FILE)['Population']

    def extract_usa_data(self, date):
        """
        Extract data for a particular date.

        Args:
            date (str): format as in DATE_FORMAT.

        Returns
        -------
            pandas.DataFrame: contains data on given date.

        """
        date = format(dt.strptime(date, self.DATE_FORMAT).date(),
                      Loader.US_DATE_FORMAT)
        data_on_date = \
            self.data_all_days.loc[self.data_all_days['Date'] == date].copy()
        column_list = ['UID', 'Confirmed', 'Deaths']
        data_on_date = data_on_date.loc[:, column_list]
        data_on_date = data_on_date.loc[data_on_date['Confirmed'] +
                                        data_on_date['Deaths'] > 7]
        return data_on_date.reset_index(drop=True)

    def extract_country_data(self, date, to_scale=False):
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
        date = format(dt.strptime(date, self.DATE_FORMAT).date(),
                      Loader.COUNTRY_DATE_FORMAT)
        data_on_date = \
            self.data_all_days.loc[self.data_all_days['Date'] == date].copy()
        column_list = ['New cases', 'New deaths', 'New recovered']
        data_on_date = data_on_date.loc[:, column_list]
        data_on_date = data_on_date.reset_index(drop=True)
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

    def get_name(self, code: int):
        """
        Get name of admin unit given its code.

        Args:
            code (int): code of admin unit.

        Returns
        -------
            str: name of admin unit.

        """
        return self.name_dict[code]
