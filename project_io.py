import pandas as pd
import numpy as np
import itertools
import datetime
import threading
import time
import sys
import urllib.request
from io import StringIO
import yfinance as yf

from project_calendar import get_valid_dates, find_nearest_date
from project_nasdaq import connect_to_nasdaq
from project_exceptions import InvalidTickerException

import warnings


#FuzzyWuzzy library raises a warning about using a slower version of a
#Levenshtein distance function. Importing the library this way catches
#and supresses the warning.
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fuzzywuzzy import fuzz

def read_file(filename):
    """Reads a CSV file into a pandas DataFrame object."""
    return pd.DataFrame(pd.read_csv(filename))

def get_api_data(api_url, data_start):
    """Converts API data into a pandas DataFrame"""
    with urllib.request.urlopen(api_url) as response:
        data = str(response.read(), 'utf-8')
        data_string = StringIO(data)
        return pd.DataFrame(pd.read_csv(data_string, header = data_start))

def check_dates(data, start_date, end_date, gui = False):
    """Checks if data is available for the entered dates. Returns nearest dates for which data is available."""
    dates = data.index.values

    if start_date not in dates or end_date not in dates:
        start_date, end_date = find_nearest_date(dates, start_date, end_date, gui)[0:2]
    return start_date, end_date

def get_data_for_period(data, reverse_data, start_date, end_date):
    """Retrieves data for a specified range of dates."""
    dates = data.index

    if not isinstance(start_date, datetime.date):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    if not isinstance(end_date, datetime.date):
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    no_dates = len(data.index)
    start_index = 0
    end_index = 0
    for i in range(no_dates):
        if dates[i] == start_date:
            start_index = i+1
        elif dates[i] == end_date:
            end_index = i
        else:
            continue

    #If the API presents data in reverse chronological order, the indices are reversed.
    if reverse_data == True:
        start_index, end_index = end_index, start_index

    return pd.DataFrame(data[start_index:end_index])

def search_for_tickers(company_names):
    """Searches for the entered tickers using the project_companies.csv reference file."""
    name_ticker_file = read_file("project_companies.csv")
    tickers, names = name_ticker_file["Symbol"].str.upper(), name_ticker_file["Name"].str.lower()
    return [tickers[i] for i in range(len(tickers)) for company_name in company_names if fuzz.ratio(names[i], company_name) >= 90]

def search_for_names(tickers_in):
    """Searches for the entered names using the project_companies.csv reference file."""
    name_ticker_file = read_file("project_companies.csv")
    tickers, names = name_ticker_file["Symbol"].str.upper(), name_ticker_file["Name"].str.lower()
    return [names[i] for i in range(len(tickers)) if tickers[i] in tickers_in]

def search_for_sector(tickers_in):
    """Searches for the sector of the entered companies using the project_companies.csv reference file.
    This is required if the NASDAQ service is selected."""
    name_ticker_file = read_file("project_companies.csv")
    tickers, names, sectors = name_ticker_file["Symbol"].str.upper(), name_ticker_file["Name"].str.lower(), name_ticker_file["Sector"].str.lower()
    return [sectors[i] for i in range(len(tickers)) if tickers[i] in tickers_in]


def format_data(data, ticker, date_column_name):
    """Converts API or archive data into a standard form."""
    #If the data date column is not called 'date', this is changed.
    if date_column_name != "date":
        data = data.rename(columns = {date_column_name: "date"})

    try:
        #Convert entries in index to datetime date objects if not already such objects.
        if not isinstance(data.index[0], datetime.datetime):
            data["date"] = pd.to_datetime(data["date"]).dt.date
        #Attaches the company ticker to the data.
        data["ticker"] = [ticker]*len(data)
        data = data.set_index("date")
        return data
    except KeyError:
        #Raise an exception if the API data does not contain the key 'date'.
        #Indicates that the ticker entered could not be found in the API data.
        raise InvalidTickerException(ticker)

def access_archive(archive_name, ticker, date_column_name, date_format = '%d/%m/%Y'):
    """Accesses the data from the archive file entered and formats the data it contains."""
    data = pd.DataFrame(pd.read_csv(archive_name))[1:]
    data[date_column_name] = pd.to_datetime(data[date_column_name], format = date_format)
    data = format_data(data, ticker, date_column_name)
    return data

# AlphaVantage API Key: NO7SX7BKV0TRLHAM
def connect_to_api(service_name, ticker, api_key, start_date, end_date, gui = False):
    """Retrieves data from the chosen API. Returns the data only for between the specified dates if
    the text interface is used. Otherwise the full data set is returned in order to compute the dates
    for the GUI invalid dates pop-up window."""

    #API details: values are in format [url, date_column_name, header_line, reverse_data]
    #reverse_data is a boolean variable. If True, the API presents data in reverse chronological
    #form and must be reversed.
    api_dict = {"alphavantage": ["https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + ticker + "&apikey=" + api_key + "&datatype=csv", "timestamp", 0, True],
    "macrotrends": ["http://download.macrotrends.net/assets/php/stock_data_export.php?t=" + ticker, "date", 9, False],
    "yahoo": False,
    "nasdaq": True,
    "archive": True}

    service_name = service_name.lower()
    while True:

        try:
            #Prevents the connection from querying the API too often.
            time.sleep(0.25)
            #Searches for API name in dictionary
            if service_name in api_dict:
                if service_name == "alphavantage":
                    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + ticker + "&apikey=" + api_key + "&datatype=csv"
                    data = get_api_data(url, api_dict[service_name][2])
                    data = format_data(data, ticker, api_dict[service_name][1])
                    if gui == False:
                        #Checks is the desired dates exist in the API data.
                        start_date, end_date = check_dates(data, start_date, end_date)
                        return get_data_for_period(data, api_dict[service_name][3], start_date, end_date), ticker, api_dict[service_name][3], start_date, end_date
                    else:
                        return data, ticker, api_dict[service_name][3], start_date, end_date
                    break

                elif service_name == "macrotrends":
                    url = "http://download.macrotrends.net/assets/php/stock_data_export.php?t=" + ticker
                    data = get_api_data(url, api_dict[service_name][2])
                    data = format_data(data, ticker, api_dict[service_name][1])
                    if gui == False:
                        start_date, end_date = check_dates(data, start_date, end_date)
                        return get_data_for_period(data, api_dict[service_name][3], start_date, end_date), ticker, api_dict[service_name][3], start_date, end_date
                    else:
                        return data, ticker, api_dict[service_name][3], start_date, end_date
                    break

                elif service_name == "yahoo":
                    #Converts start and end dates to datetime date objects as this is the form
                    #that yfinance data stores dates.
                    if not isinstance(start_date, datetime.date):
                        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

                    start_date = datetime.datetime.strftime(start_date, '%Y-%m-%d')
                    end_date += datetime.timedelta(days=1)
                    end_date = datetime.datetime.strftime(end_date, '%Y-%m-%d')

                    if start_date == "":
                        yf_dataframe = yf.Ticker(ticker).history(period="max")
                    else:
                        yf_dataframe = yf.Ticker(ticker).history(start = start_date, end = end_date)

                    if len(yf_dataframe) == 0:
                        raise InvalidTickerException(ticker)

                    #Formatting yfinance data.
                    yf_dataframe.columns = yf_dataframe.columns.str.lower()
                    yf_dataframe.index = pd.to_datetime(yf_dataframe.index)
                    yf_dataframe.index = [d.date() for d in yf_dataframe.index]

                    return yf_dataframe, ticker, False, start_date, end_date
                    break

                elif service_name == "nasdaq":
                    name = search_for_names(ticker)
                    sector = search_for_sector(ticker)
                    words = name[0].split()

                    #Formatting company name so it can be used to query the NASDAQ historical stock data.
                    if len(words) > 1:
                        name = ""
                        for i in range(len(words)):
                            if i != len(words) - 1:
                                name += words[i].capitalize() + "%25252520"
                            else:
                                name += words[i].capitalize()

                    #Due to access requirements, the connect_to_nasdaq function needs the company sector
                    #to retrieve data.
                    nasdaq_dataframe = connect_to_nasdaq(ticker, name[0], sector[0])
                    nasdaq_dataframe = format_data(nasdaq_dataframe, ticker, "date")

                    if gui == False:
                        start_date, end_date = check_dates(nasdaq_dataframe, start_date, end_date)
                        return get_data_for_period(nasdaq_dataframe, True, start_date, end_date), ticker, True, start_date, end_date
                    else:
                        return nasdaq_dataframe, ticker, True, start_date, end_date
                    break

                elif service_name == "archive":
                    #Converts archive data into standard form.
                    data = pd.DataFrame(pd.read_csv(archive_name, parse_dates = [date_column_name]))[1:]
                    data = format_data(data, self.ticker_list[0], self.date_column_name)

            #If the API name is not in the dictionary, a NameError is raised.
            else:
                raise NameError
        #The user is repeatedly asked for a valid API until the input matches one of the
        #APIs in the dictionary.
        except NameError:
            print("Please enter a valid API: AlphaVantage, MacroTrends, Yahoo, NASDAQ, Archive")
            service_name = input("Enter the service name from which to retrieve data for the period " + start_date + " to " + end_date +": >")
        #If the company ticker is invalid, an exception is raised.
        except InvalidTickerException as e:
            print(e.message)
            if isinstance(start_date, datetime.date):
                start_date = datetime.datetime.strftime(start_date, '%Y-%m-%d')
            if isinstance(end_date, datetime.date):
                end_date = datetime.datetime.strftime(end_date, '%Y-%m-%d')
            ticker = input("Enter the ticker name from which to retrieve data for the period " + start_date + " to " + end_date +": >")
