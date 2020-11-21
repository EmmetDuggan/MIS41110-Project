# from project_io import connect_to_api, search_for_tickers, get_data_for_period
from project_io import connect_to_api, get_data_for_period
from project_calendar import get_valid_dates, find_nearest_date
from project_descriptive_stats import compute_descriptive_stats, make_stats_frame, dictionary_values_to_series, add_to_frame
#from project_gui import ask_for_date_selection
import datetime
import pandas as pd

class DataUnavailableException(Exception):
    ticker = ""
    date = ""
    def __init__(self, ticker, date):
            self.message = "Data unavailable for \"" + ticker + "\" for the date: " + date
            self.ticker = ticker
            self.date = date
            super().__init__(self.message)

class MultiDataUnavailableException(Exception):
    exceptions = []
    tickers = []
    def __init__(self):
        self.message = "Multiple companies have limited data."
        super().__init__(self.message)

    def add_exception(self, exception, ticker):
        self.exceptions.append(exception)
        self.tickers.append(ticker)


#Function to create a DataFrame for a single company.
def make_single_frame(service_name, ticker, start_date = None, end_date = None, gui = False):
    if gui == False:
        start_date, end_date = get_valid_dates()

    if service_name != "yahoo":
        data, date_column_name, reverse_data, new_start, new_end = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)
        data = get_data_for_period(data, date_column_name, reverse_data, start_date, end_date)

        if reverse_data == True:
            data = data.iloc[::-1]

        stats = compute_descriptive_stats(data["close"])
        stats_frame = make_stats_frame(stats, ticker)
        return stats_frame, data, date_column_name, reverse_data, start_date, end_date
    else:
        yf_data = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)
        dates = [datetime.datetime.strftime(date, '%Y-%m-%d') for date in yf_data.index]
        stats = compute_descriptive_stats(yf_data["close"])
        stats_frame = make_stats_frame(stats, ticker)
        return stats_frame, yf_data, "yahoo", False, start_date, end_date

def add_to_frame(stats, ticker, frame):
    frame[ticker] = dictionary_values_to_series(stats)
    return frame

#Function to add company descriptive statistics to a DataFrame.
def add_companies_to_frame(service_name, start_date, end_date, frame):
    tickers = parse_tickers(input("Enter the list of tickers, seperated by a space: >"))
    data_sets = []
    for ticker in tickers:
        data = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date)[0]
        data_sets.append(data)
        stats = compute_descriptive_stats(data["open"])
        add_to_frame(stats, ticker, frame)
    return frame, data_sets

#Function to create a DataFrame for multiple companies.
def make_full_frame(service_name, tickers, start_date = None, end_date = None, gui = False):
    data_sets = []

    #An initial DataFrame is created using the first company ticker.
    if gui == False:
        frame, data, date_column_name, reverse_data, start_date, end_date = make_single_frame(service_name, tickers[0])
    else:
        frame, data, date_column_name, reverse_data, start_date, end_date = make_single_frame(service_name, tickers[0], start_date, end_date, gui)

    data_sets.append(data)
    index = 1
    unavailable_index_date = []
    #For each ticker in the list, the company statistics are computed and added
    #to the existing DateFrame.
    for ticker in tickers[1:]:
        if service_name != "yahoo":
            data = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)[0]
            if start_date in list(data[date_column_name]):
                data = get_data_for_period(data, date_column_name, reverse_data, start_date, end_date)
                print("Same length")

            else:
                print("Not same length")
                print(len(data))
                start_date = data[date_column_name].iloc[-1::].item()
                print("Start:",start_date)
                print("End:",end_date)
                data = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)[0]
                data = get_data_for_period(data, date_column_name, reverse_data, start_date, end_date)
                unavailable_index_date.append((index, start_date))

            print(len(data))
            print("Data: ",data)
            index += 1

        else:
            data = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)
            print(data)

            if start_date not in data.index:
                print("Dates are not ok")
                start_date = datetime.datetime.strftime(pd.to_datetime(data.index[0]), '%Y-%m-%d')
                unavailable_index_date.append((index, start_date))

            date_column_name = "yahoo"

        if reverse_data == True:
            data = data.iloc[::-1]

        data_sets.append(data)
        stats = compute_descriptive_stats(data["close"])
        add_to_frame(stats, ticker, frame)

    print("Data Sets from make_full_frame: ", data_sets)

    #The DataFrame containing the statistics of all companies is returned along
    #with the data for the period and tickers.
    return frame, data_sets, tickers, unavailable_index_date
