from project_io import connect_to_api, search_for_tickers
from project_calendar import get_valid_dates, find_nearest_date
from project_data_visualisation import plot_single_time_series, plot_multiple_time_series
from project_descriptive_stats import compute_descriptive_stats, make_stats_frame, add_to_frame
import numpy as np

#Function to repeatedly ask for a yes-or-no answer.
def ask_yes_or_no(question):
    answer = input(question).lower()
    valid_answers = ["y", "n"]
    while True:
        try:
            if answer in valid_answers:
                return answer
                break
            else:
                raise ValueError
        except ValueError:
            print("Please enter only \'y\' or \'n\'.")
            answer = input(question).lower()

def ask_ticker_or_name():
    answer = input("Would you like to search by company ticker or company name?\nEnter \'T\' or \'N\' to query by ticker or name, respectively: >").lower()
    valid_answers = ["t", "n"]
    while True:
        try:
            if answer in valid_answers:
                return answer
                break
            else:
                raise ValueError
        except ValueError:
            print("Please enter only \'T\' or \'N\'.")
            answer = input(question).lower()

#Function to select which analysis user wishes to carry out.
def print_menu():
    answer = input("Select one of the following options:\n1. Analysis of Single Company.\n2. Analysis of Multiple Companies.\t>")
    valid_answers = ["1", "2"]
    while True:
        try:
            if answer in valid_answers:
                return answer
                break
            else:
                raise ValueError
        except ValueError:
            print("Please enter only \'1\' or \'2\'.")
            answer = input("Select one of the following options:\n1. Analysis of Single Company.\n2. Analysis of Multiple Companies.\n")

#Function to covert list of tickers seperated for a space into list of
#capitalised tickers.
def parse_tickers(ticker_list_in):
    tickers = ticker_list_in.split(" ")
    return [ticker.upper() for ticker in tickers]

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

#def make_single_frame(service_name, ticker, start_date = None, end_date = None):
#Function to create a DataFrame for a single company.
def make_single_frame(service_name, ticker):
    start_date, end_date = get_valid_dates()
    data, date_column_name, reverse_data, new_start, new_end = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date)
    stats = compute_descriptive_stats(data["open"])
    stats_frame = make_stats_frame(stats, ticker)
    return stats_frame, data, date_column_name, new_start, new_end

#Function to create a DataFrame for multiple companies.
def make_full_frame(service_name, tickers, start_date = None, end_date = None):
    #Listed of tickers typed by user is parsed.
    #tickers = parse_tickers(input("Enter the list of tickers, seperated by a space: >"))
    data_sets = []
    #An initial DataFrame is created using the first company ticker.
    frame, data, date_column_name, start_date, end_date = make_single_frame(service_name, tickers[0])
    #For each ticker in the list, the company statistics are computed and added
    #to the existing DateFrame.
    for ticker in tickers:
        data, date_column_name, reverse_data, new_start, new_end = connect_to_api(service_name, ticker, "NO7SX7BKV0TRLHAM", start_date, end_date)
        data_sets.append(data)
        stats = compute_descriptive_stats(data["open"])
        add_to_frame(stats, ticker, frame)
    #The DataFrame containing the statistics of all companies is returned along
    #with the data for the period and tickers.
    return frame, data_sets, tickers

def main():
    service_name = input("Enter the service name: >")
    menu_selection = print_menu()
    ticker_name_choice = ask_ticker_or_name()
    if menu_selection == "1":
        if ticker_name_choice == "t":
            ticker = input("Enter the company ticker: >")
        else:
            ticker = search_for_tickers(input("Enter the full company name: >"))[0]
        frame, data, date_column_name, start_date, end_date = make_single_frame(service_name, ticker)
        plot_single_time_series(data, ticker, date_column_name, True)
    if menu_selection == "2":
        if ticker_name_choice == "t":
            tickers = input("Enter the company ticker: >")
        else:
            tickers = search_for_tickers(input("Enter the full company names, seperated by a semi-colon (;): >").split("; "))
        print(tickers)
        frame, data_sets, tickers = make_full_frame(service_name, tickers)
        plot_multiple_time_series(data_sets, tickers, "timestamp")

    print(frame)

    #time_series(data, ticker, date_column_name, True)

if __name__ == '__main__':
    main()
