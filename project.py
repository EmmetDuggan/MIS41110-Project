from project_io import search_for_tickers
from project_data_visualisation import plot_raw_time_series, plot_linear_regression, plot_time_series_forecasts
from project_frames import make_single_frame, add_to_frame, make_full_frame
from project_gui import MenuWindow
from project_text import TextInterface, loading_symbol
from project_calendar import validate_future_date
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
import threading

#Function to repeatedly ask for a yes-or-no answer.
def ask_question(question, valid_answers):
    """Keeps asking the user a question until the input matches
    one of the valid answers provided"""
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

def check_if_archive_exists(filename):
    """Checks to see if the entered file name exists in the path or current directory."""
    while True:
        try:
            f = open(filename)
            break
        except FileNotFoundError:
            print("The entered file name was not found. Please ensure the file path is correct or that the file is in the current directory.")
            filename = input("Please re-enter the file path or name: >")

def plot_data_text_interface(service_name, data_sets, tickers, period, steps, future_date):
    """Plots the linear regression and ARIMA forecasts from the text interface."""
    if service_name == "alphavantage":
        period = "d"

    linear_plot, rmse, r2, linear_min, linear_max = plot_linear_regression(data_sets, tickers, future_date, period, steps)
    arima_plot, rmse_list, r2_list, linear_min, linear_max, arima_min, arima_max = plot_time_series_forecasts(data_sets, tickers, future_date, period, steps)
    if len(data_sets) == 1:
        return (linear_plot, arima_plot), rmse, r2, linear_min, linear_max, arima_min, arima_max
    else:
        return (linear_plot, arima_plot), rmse_list, r2_list, linear_min, linear_max, arima_min, arima_max

def save_data(data_to_save, plot_to_save):
    """Asks the user if they wish to save the data."""
    ans = ask_question("Would you like to save the results? If not, the programme will end. (y/n) >", ["y","n"])
    if ans == "y":
        name = input("Enter the file name to which the results are to be saved.\nNote that plots are saved in PDF format and results as CSV files. >")
        data_to_save.to_csv(name + ".csv")
        plot_to_save.savefig(name + ".pdf")

def notify_of_data_limit_text_interface(tickers, unavailable_index_date, start_date):
    """Equivalent to the 'notify_of_data_limit' function in the 'project_gui' module.
    Notifies the user if one of the companies' data does not go back as far as the first company which was entered."""
    if len(unavailable_index_date) != 0:
        for index, date in unavailable_index_date:
            print("Note: Data is not available for \"{}\" for the date {}. Data is only available from {} onwards; plotted data and computed statistics for the company are shown from this date.".format(tickers[index], start_date, date))


def main():
    """Runs the programme."""

    interface_selection = ask_question("Would you like to launch the graphical user interface or use the text interface instead?\nEnter \"GUI\" or \"Text\": >", ["gui", "text"])
    if interface_selection == "gui":
        gui = MenuWindow()

    else:
        text = TextInterface()
        text.show_markdown()
        service_name = text.ask_api()

        #If an API is selected:
        if service_name != "archive":
            number_companies = text.ask_single_or_multiple()
            ticker_name_choice, companies_input = text.ask_tickers_or_names()

            if number_companies == "1":
                if ticker_name_choice == "t":
                    ticker = companies_input.upper().split(";")[0]
                else:
                    ticker = search_for_tickers([companies_input.lower().split(";")])[0]

                period_choice = text.ask_dates()
                stats_frame, data, ticker, reverse_data, start_date, end_date = make_single_frame(service_name, ticker, gui = False)
                #Table does not quite print properly so is not called.
                #text.show_descriptive_stats(stats_frame)
                future_date = input("Enter the date for which you would like to predict the stock price (yyyy-mm-dd): >")
                future_date = validate_future_date(future_date)

                #Loading symbol function does not properly thread so is not called.
                # finished = False
                # t = threading.Thread(target=loading_symbol, args=(finished,), daemon = True)
                # t.start()

                print("Making forecasts...")
                plots, rmse_list, r2_list, linear_min, linear_max, arima_min, arima_max = plot_data_text_interface(service_name, [data], [ticker], period_choice, 20, future_date)
                model_result = pd.DataFrame([rmse_list, r2_list, linear_min[0], linear_max[0], arima_min[0], arima_max[0]],
                                            index = ["RMSE", "R^2", "Linear Regression: Minimum","Linear Regression: Maximum","ARIMA: Minimum","ARIMA: Maximum",],
                                            columns = [ticker])
                stats_frame = stats_frame.append(model_result)

                # finished = True
                print("")

                print(stats_frame)
                for plot in plots:
                    plt.show()

                text.export_data(stats_frame, plots[1])
                text.close_interface()

            if number_companies == "2":
                if ticker_name_choice == "t":
                    tickers = companies_input.upper().split(";")
                else:
                    tickers = search_for_tickers(companies_input.lower().split(";"))

                period_choice = text.ask_dates()
                if period_choice == "m":
                    period_choice = "MS"

                stats_frame, data_sets, tickers, unavailable_index_date, start_date = make_full_frame(service_name, tickers)
                future_date = input("Enter the date for which you would like to predict the stock price (yyyy-mm-dd): >")
                future_date = validate_future_date(future_date)

                notify_of_data_limit_text_interface(tickers, unavailable_index_date, start_date)

                # finished = False
                # t = threading.Thread(target=loading_symbol, args=(finished,), daemon = True)
                # t.start()

                print("Making forecasts...")
                plots, rmse_list, r2_list, linear_min, linear_max, arima_min, arima_max = plot_data_text_interface(service_name, data_sets, tickers, period_choice, 20, future_date)
                model_result = pd.DataFrame([rmse_list, r2_list, linear_min, linear_max, arima_min, arima_max],
                                            index = ["RMSE", "R^2", "Linear Regression: Minimum","Linear Regression: Maximum","ARIMA: Minimum","ARIMA: Maximum",],
                                            columns = tickers)
                stats_frame = stats_frame.append(model_result)

                # finished = True
                print("")

                for plot in plots:
                    plt.show()
                finished = True
                print(stats_frame)

                text.export_data(stats_frame, plots[1])
                text.close_interface()



        else:
            archive_name = input("\nEnter the archive file name: >")
            check_if_archive_exists(archive_name)
            with open(archive_name) as archive:
                csv_contents = csv.reader(archive, delimiter = ",")
                rows = [row for row in csv_contents]

            columns = rows[0]
            ticker = input("\nEnter the company ticker: >").upper()

            date_format, date_column_name = text.ask_archive_date_format()
            period_choice = text.ask_dates()

            stats_frame, data = make_single_frame(service_name, ticker, filename = archive_name, date_column_name = date_column_name, date_format = date_format)[0:2]
            future_date = input("Enter the date for which you would like to predict the stock price (yyyy-mm-dd): >")
            future_date = validate_future_date(future_date)

            # finished = False
            # t = threading.Thread(target=loading_symbol, args=(finished,), daemon = True)
            # t.start()

            print("Making forecasts...")
            plots, rmse, r2, linear_min, linear_max, arima_min, arima_max = plot_data_text_interface(service_name, [data], [ticker], period_choice, 20, future_date)
            model_result = pd.DataFrame([rmse, r2, linear_min[0], linear_max[0], arima_min[0], arima_max[0]],
                                        index = ["RMSE", "R^2", "Linear Regression: Minimum","Linear Regression: Maximum","ARIMA: Minimum","ARIMA: Maximum",],
                                        columns = [ticker])
            stats_frame = stats_frame.append(model_result)

            # finished = True
            print("")

            for plot in plots:
                plt.show()

            print(stats_frame)

            text.export_data(stats_frame, plots[1])
            text.close_interface()




if __name__ == '__main__':
    main()
