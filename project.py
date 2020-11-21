#from project_io import search_for_tickers
from project_data_visualisation import plot_raw_time_series, plot_linear_regression
from project_frames import make_single_frame, add_to_frame, make_full_frame
from project_gui import MenuWindow

import numpy as np

#Function to repeatedly ask for a yes-or-no answer.
def ask_question(question, valid_answers):
    answer = input(question).lower()
    while True:
        try:
            if answer in valid_answers:
                return answer
                break
            else:
                raise ValueError
        except ValueError:
            print("Please enter only one of: ", end = "")
            for ans in valid_answers[:len(valid_answers)-1]:
                print(ans.replace("\'", "") + ", ", end = "")
            print(valid_answers[-1])
            answer = input(question).lower()

def main():
    interface_selection = ask_question("Would you like to launch the graphical user interface or use the text interface instead?\nEnter \"GUI\" or \"Text\": >", ["gui", "text"])
    if interface_selection == "gui":
        gui = MenuWindow()

    else:
        service_name = input("Enter the service name: >")
        menu_selection = ask_question("Select one of the following options:\n1. Analysis of Single Company.\n2. Analysis of Multiple Companies. >", ["1","2"])
        ticker_name_choice = ask_question("Would you like to search by company ticker or company name?\nEnter \'T\' or \'N\' to query by ticker or name, respectively: >", ["t","n"])
        if menu_selection == "1":
            if ticker_name_choice == "t":
                ticker = input("Enter the company ticker: >")
            else:
                ticker = search_for_tickers(input("Enter the full company name: >"))[0]
            frame, data, date_column_name, reverse_data, start_date, end_date = make_single_frame(service_name, ticker)
            if service_name != "yahoo":
                plot_raw_time_series(data, ticker, date_column_name, True)
            else:
                plot_raw_time_series(data, ticker, date_column_name, True, yahoo = True)
        if menu_selection == "2":
            if ticker_name_choice == "t":
                tickers = input("Enter the company tickers, seperated by a semi-colon (;): >").split("; ")
            else:
                tickers = search_for_tickers(input("Enter the full company names, seperated by a semi-colon (;): >").split("; "))
            frame, data_sets, tickers = make_full_frame(service_name, tickers)
            plot_linear_regression(data_sets, tickers, "timestamp")


        print(frame)

if __name__ == '__main__':
    main()

# main()
