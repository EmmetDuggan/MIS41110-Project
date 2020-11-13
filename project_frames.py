from project_io import connect_to_api, search_for_tickers
from project_calendar import get_valid_dates, find_nearest_date
from project_descriptive_stats import compute_descriptive_stats, make_stats_frame, dictionary_values_to_series, add_to_frame

import datetime

#Function to create a DataFrame for a single company.
def make_single_frame(service_name, ticker, start_date = None, end_date = None, gui = False):
    if gui == False:
        start_date, end_date = get_valid_dates()

    if service_name != "yahoo":

        data, date_column_name, reverse_data, new_start, new_end = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)
        stats = compute_descriptive_stats(data["open"])
        stats_frame = make_stats_frame(stats, ticker)
        return stats_frame, data, date_column_name, new_start, new_end
    else:
        yf_data = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)
        dates = [datetime.datetime.strftime(date, '%Y-%m-%d') for date in yf_data.index]
        stats = compute_descriptive_stats(yf_data["open"])
        stats_frame = make_stats_frame(stats, ticker)
        return stats_frame, yf_data, dates, start_date, end_date

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
    #Listed of tickers typed by user is parsed.
    #tickers = parse_tickers(input("Enter the list of tickers, seperated by a space: >"))
    data_sets = []
    # if service_name != "yahoo":
        #An initial DataFrame is created using the first company ticker.
    if gui == False:
        frame, data, date_column_name, start_date, end_date = make_single_frame(service_name, tickers[0])
    else:
        frame, data, date_column_name, start_date, end_date = make_single_frame(service_name, tickers[0], start_date, end_date, gui)
    #For each ticker in the list, the company statistics are computed and added
    #to the existing DateFrame.
    for ticker in tickers:
        if service_name != "yahoo":
            data = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)[0]
        else:
            data = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)
        data_sets.append(data)
        stats = compute_descriptive_stats(data["open"])
        add_to_frame(stats, ticker, frame)
    #The DataFrame containing the statistics of all companies is returned along
    #with the data for the period and tickers.
    return frame, data_sets, tickers
