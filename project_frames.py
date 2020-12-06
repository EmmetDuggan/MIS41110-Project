from project_io import connect_to_api, get_data_for_period, access_archive, check_dates
from project_calendar import get_valid_dates
from project_descriptive_stats import compute_descriptive_stats, make_stats_frame, dictionary_values_to_series, add_to_frame
from project_exceptions import DataUnavailableException, MultiDataUnavailableException
import datetime
import pandas as pd

def make_single_frame(service_name, ticker, start_date = None, end_date = None, gui = False, filename = None, date_column_name = "date", date_format = '%d/%m/%Y'):
    """Creates a DataFrame containing the descriptive statistics relating to a single company."""
    if gui == False:
        start_date, end_date = get_valid_dates()

    if service_name == "archive":
        #Convert archive data into a standard form.
        date_format = date_format.replace("y", "Y")
        data = access_archive(filename, ticker, date_column_name, date_format)
        new_start, new_end = check_dates(data, start_date, end_date, gui = False)
        data = get_data_for_period(data, True, new_start, new_end)
        stats = compute_descriptive_stats(data["close"])
        stats_frame = make_stats_frame(stats, ticker)
        return stats_frame, data, True, start_date, end_date

    else:
        #Connect to the API and ensure data is available for the entered dates.
        data, ticker, reverse_data, new_start, new_end = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)
        new_start, new_end = check_dates(data, start_date, end_date, gui = False)

        if gui == True:
            data = get_data_for_period(data, reverse_data, start_date, end_date)

        #Reverses order of data if API presents data in form of most recent dates first.
        if reverse_data == True:
            data = data.iloc[::-1]

        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        stats = compute_descriptive_stats(data["close"])
        stats_frame = make_stats_frame(stats, ticker)
        return stats_frame, data, ticker, reverse_data, start_date, end_date

def add_to_frame(stats, ticker, frame):
    """Adds the statistics from a company to an existing DataFrame."""
    frame[ticker] = dictionary_values_to_series(stats)
    return frame

#Function to add company descriptive statistics to a DataFrame.
# def add_companies_to_frame(service_name, start_date, end_date, frame):
#     tickers = parse_tickers(input("Enter the list of tickers, seperated by a space: >"))
#     data_sets = []
#     for ticker in tickers:
#         data = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date)[0]
#         data_sets.append(data)
#         stats = compute_descriptive_stats(data["close"])
#         add_to_frame(stats, ticker, frame)
#     return frame, data_sets

def make_full_frame(service_name, tickers, start_date = None, end_date = None, gui = False):
    """Creates a DataFrame containing the descriptive statistics relating to a several companies."""
    data_sets = []

    #An initial DataFrame is created using the first company ticker.
    if gui == False:
        frame, data, ticker, reverse_data, original_start_date, end_date = make_single_frame(service_name, tickers[0])
        #MacroTrends data does not include end dates of period. This must be checked for.
        start_date = original_start_date
        start_date_minus_one = start_date - datetime.timedelta(days=1)
    else:
        frame, data, ticker, reverse_data, original_start_date, end_date = make_single_frame(service_name, tickers[0], start_date, end_date, gui)
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    data_sets.append(data)
    index = 1
    unavailable_index_date = []
    new_tickers = [ticker.upper()]

    #For each ticker in the list, the company statistics are computed and added
    #to the existing DateFrame.
    for ticker in tickers[1:]:
        data, ticker = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", original_start_date, end_date, gui)[0:2]

        #Check that the API data matches that of the first company.
        if start_date or start_date_minus_one in data.index.values:
            data = get_data_for_period(data, reverse_data, original_start_date, end_date)

        #If the data is different (data is limited for this particular company compared to the
        #first company), an exception is raised. Appends information about the limited data to the
        #unavailable_index_date list.
        else:
            start_date = data.index[0]
            data, ticker = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date, gui)[0:2]
            data = get_data_for_period(data, reverse_data, start_date, end_date)
            if start_date != data_sets[0].index[0]:
                unavailable_index_date.append((index, start_date))

        if reverse_data == True:
            data = data.iloc[::-1]

        data_sets.append(data)
        new_tickers.append(ticker.upper())
        stats = compute_descriptive_stats(data["close"])
        add_to_frame(stats, ticker, frame)
        index += 1

    #The DataFrame containing the statistics of all companies is returned along
    #with the data for the period and tickers.
    if gui == False:
        return frame, data_sets, new_tickers, unavailable_index_date, original_start_date
    else:
        return frame, data_sets, new_tickers, unavailable_index_date
