import pandas as pd
import urllib.request
from io import StringIO
import yfinance as yf
from project_calendar import get_valid_dates, find_nearest_date

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
def check_dates(data, date_column_name, start_date, end_date):
    dates = data[date_column_name]
    start_date, end_date = find_nearest_date(dates, start_date, end_date)
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


# https://stackoverflow.com/questions/47379476/how-to-convert-bytes-data-into-a-python-pandas-dataframe
# AlphaVantage API Key: NO7SX7BKV0TRLHAM
def connect_to_api(service_name, ticker, api_key, start_date, end_date):

    # start_date, end_date = get_valid_dates()

    #API details: values are in format [url, date_column_name, header_line, reverse_data]
    #reverse_data is a boolean variable. If True, the API presents data in reverse chronological
    #form and must be reversed.
    api_dict = {"alphavantage": ["https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + ticker + "&apikey=" + api_key + "&datatype=csv", "timestamp", 0, True],
    "financial content": ["http://markets.financialcontent.com/stocks/action/gethistoricaldata?Month=12&Symbol=" + ticker + "&Range=300&Year=2017", 0],
    "wall street journal": ["http://quotes.wsj.com/" + ticker + "/historical-prices/download?MOD_VIEW=page&num_rows=6299.041666666667&range_days=6299.041666666667&startDate=09/06/2000&endDate=12/05/2017", 0],
    "macrotrends": ["http://download.macrotrends.net/assets/php/stock_data_export.php?t=" + ticker, "date", 9, False]}

    service_name = service_name.lower()
    while True:
        try:
            #Searches for API name in dictionary
            if service_name in api_dict:
                data = get_api_data(api_dict[service_name][0], api_dict[service_name][2])
                if '{' in data.keys():
                    return None, None, None
                    break
                else:
                    new_start, new_end = check_dates(data, api_dict[service_name][1], start_date, end_date)
                    return get_data_for_period(data, api_dict[service_name][1], new_start, new_end), api_dict[service_name][1], api_dict[service_name][3], new_start, new_end
                    break
            elif service_name == "yahoo":
                return yf.Ticker(ticker).history(start = start_date, end = end_date)
                break
            #If the API name is not in the dictionary, a NameError is raised.
            else:
                raise NameError
        #The user is repeatedly asked for a valid API until the input matches one of the
        #APIs in the dictionary.
        except NameError:
            print("Please enter a valid API:", api_dict.keys())
            service_name = input("Enter the service name from which to retrieve data for the period " + start_date + " to " + end_date +": >")
