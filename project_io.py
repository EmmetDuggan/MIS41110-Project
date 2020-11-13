import pandas as pd
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

import warnings

#FuzzyWuzzy library raises a warning about using a slower version of a
#Levenshtein distance function. Importing the library this way catches
#and supresses the warning.
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fuzzywuzzy import fuzz

#Function to read csv files into a Pandas DataFrame.
def read_file(filename):
    return pd.DataFrame(pd.read_csv(filename))

#Function to convert API data into a Pandas DataFrame
def get_api_data(api_url, data_start):
    with urllib.request.urlopen(api_url) as response:
        data = str(response.read(), 'utf-8')
        data_string = StringIO(data)
        return pd.DataFrame(pd.read_csv(data_string, header = data_start))

#Function to return nearest dates for which data is available.
def check_dates(data, date_column_name, start_date, end_date, gui = False):
    if date_column_name != "yahoo":
        dates = data[date_column_name]
    else:
        dates = [datetime.datetime.strftime(date, '%Y-%m-%d') for date in data.index]

    if start_date not in dates or end_date not in dates:
        start_date, end_date = find_nearest_date(dates, start_date, end_date, gui)[0:2]
    return start_date, end_date

#Function to retrieve data for a specified range of dates.
def get_data_for_period(data, date_column_name, start_date, end_date):
    dates = data[date_column_name]
    no_dates = len(dates)
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
    if start_index > end_index:
        start_index, end_index = end_index, start_index

    return pd.DataFrame(data[start_index:end_index])

def search_for_tickers(company_names):
    name_ticker_file = read_file("project_companies.csv")
    tickers, names = name_ticker_file["Symbol"].str.upper(), name_ticker_file["Name"].str.lower()
    return [tickers[i] for i in range(len(tickers)) for company_name in company_names if fuzz.ratio(names[i], company_name) >= 80]

def search_for_names(tickers_in):
    name_ticker_file = read_file("project_companies.csv")
    tickers, names = name_ticker_file["Symbol"].str.upper(), name_ticker_file["Name"].str.lower()
    company_names = []
    return [names[i] for i in range(len(tickers)) if tickers[i] in tickers_in]

def search_for_sector(tickers_in):
    name_ticker_file = read_file("project_companies.csv")
    tickers, names, sectors = name_ticker_file["Symbol"].str.upper(), name_ticker_file["Name"].str.lower(), name_ticker_file["Sector"].str.lower()
    return [sectors[i] for i in range(len(tickers)) if tickers[i] in tickers_in]


    #return [tickers[i] for i in range(len(tickers)) if names[i] in company_names]

#name_ticker_file[(name_ticker_file.Symbol == {symbol}) | name_ticker_file.Name == {name}]
#fuzzywuzzy library
#df[df['Symbol'].str.contains('Zyn')]
#Implement GUI

def search_archive(archive_file, tickers, ):
    archive = read_file(archive_file)

def loading(finish):
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if finish:
            break
        sys.stdout.write('\rloading ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')

# https://stackoverflow.com/questions/47379476/how-to-convert-bytes-data-into-a-python-pandas-dataframe
# AlphaVantage API Key: NO7SX7BKV0TRLHAM
def connect_to_api(service_name, ticker, api_key, start_date, end_date, gui = False):

    # finish=False
    # t = threading.Thread(target=loading(finish))
    # t.start()

    #API details: values are in format [url, date_column_name, header_line, reverse_data]
    #reverse_data is a boolean variable. If True, the API presents data in reverse chronological
    #form and must be reversed.
    api_dict = {"alphavantage": ["https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + ticker + "&apikey=" + api_key + "&datatype=csv", "timestamp", 0, True],
    #"nasdaq": ["https://www.nasdaq.com/api/v1/historical/" + ticker + "/stocks/" + start_date + "/" + end_date, "Date", 0, True],
    "macrotrends": ["http://download.macrotrends.net/assets/php/stock_data_export.php?t=" + ticker, "date", 9, False]}

    service_name = service_name.lower()

    while True:
        try:
            #Searches for API name in dictionary
            print("Service: ",service_name)
            if service_name in api_dict:
                data = get_api_data(api_dict[service_name][0], api_dict[service_name][2])
                if "{" not in data.keys():

                    if gui == False:
                        start_date, end_date = check_dates(data, api_dict[service_name][1], start_date, end_date)
                        return get_data_for_period(data, api_dict[service_name][1], start_date, end_date), api_dict[service_name][1], api_dict[service_name][3], start_date, end_date
                    else:
                        return data, api_dict[service_name][1], api_dict[service_name][3], start_date, end_date
                    break
            elif service_name == "yahoo":
                #Yahoo-ticker-downloader
                #Yahoo! Finance returns data in slightly different format. Column containing
                #date information is not among actual DataFrame columns. Entry indices contain
                #information about the data date.
                end_date_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                end_date_dt += datetime.timedelta(days=1)
                end_date = datetime.datetime.strftime(end_date_dt, '%Y-%m-%d')

                yf_dataframe = yf.Ticker(ticker).history(start = start_date, end = end_date)
                yf_dataframe.columns = yf_dataframe.columns.str.lower()

                return yf_dataframe
                break

            elif service_name == "nasdaq":
                name = search_for_names(ticker)
                sector = search_for_sector(ticker)
                print(sector)
                words = name[0].split()

                if len(words) > 1:
                    name = ""
                    for i in range(len(words)):
                        if i != len(words) - 1:
                            name += words[i].capitalize() + "%25252520"
                        else:
                            name += words[i].capitalize()
                print(connect_to_nasdaq(ticker, name, sector[0]))
                #return connect_to_nasdaq(ticker, name, sector)
                break

                #return connect_to_nasdaq(ticker,)
            #If the API name is not in the dictionary, a NameError is raised.
            else:
                raise NameError
        #The user is repeatedly asked for a valid API until the input matches one of the
        #APIs in the dictionary.
        except NameError:
            print("Please enter a valid API:", api_dict.keys())
            service_name = input("Enter the service name from which to retrieve data for the period " + start_date + " to " + end_date +": >")

    # finish=True
