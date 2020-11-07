from project_io import search_for_tickers
from project_data_visualisation import plot_single_time_series, plot_multiple_time_series
from project_frames import make_single_frame, add_to_frame, make_full_frame
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
            tickers = input("Enter the company tickers, seperated by a semi-colon (;): >").split("; ")
        else:
            tickers = search_for_tickers(input("Enter the full company names, seperated by a semi-colon (;): >").split("; "))
        frame, data_sets, tickers = make_full_frame(service_name, tickers)
        plot_multiple_time_series(data_sets, tickers, "timestamp")

    print(frame)

    #time_series(data, ticker, date_column_name, True)

if __name__ == '__main__':
    main()
