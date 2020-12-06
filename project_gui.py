from project_io import connect_to_api, search_for_tickers, check_dates, format_data, access_archive
from project_calendar import find_nearest_date
from project_data_visualisation import plot_raw_time_series, plot_linear_regression, plot_time_series_forecasts
from project_descriptive_stats import compute_descriptive_stats, make_stats_frame, add_to_frame
from project_frames import make_single_frame, make_full_frame, DataUnavailableException, MultiDataUnavailableException
import datetime
import time
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk


class MenuWindow():

    def __init__(self, master=None):
        """Initialises parameters/appearance of the GUI MenuWindow object."""
        self.root = tk.Tk()
        self.root.wm_title("Price Predictor GUI")

        self.s = ttk.Style()
        self.s.configure("TButton", font=("Calibri", 10), foreground = 'grey12', background = 'white')
        self.s.configure("TLabel", font=("Calibri",10), foreground = 'white', weight="bold", background = 'grey12')
        self.s.configure("TLabelframe", background = 'grey12', labelanchor='n')

        self.add_api_panel()
        self.add_ticker_panel()
        self.add_period_panel()
        self.add_retrieve_button()

        self.root.config(bg='grey12')
        self.root.geometry("350x400")
        self.root.mainloop()

        self.stats_frame = pd.DataFrame()
        self.data_sets = []
        self.tickers_chosen = False
        self.ticker_list = []
        self.name_list = []
        self.service_name = ""
        self.archive_name = ""
        self.start_date = ""
        self.end_date = ""
        self.option_dates = []
        self.future_date = ""
        self.period = ""

    def add_api_panel(self):
        """Creates a panel to obtain user input regarding the service they wish to use.
        Composed of buttons for each API, a button to query an archive and a button which
        provides details about the API services."""
        api_panel = ttk.LabelFrame(self.root, text="  Service Name  ", style = "TLabelframe", labelanchor='n')

        global alphavantage_button, macrotrends_button, yahoo_button, nasdaq_button, archive_button
        alphavantage_button = tk.Button(api_panel, text="AlphaVantage", command = lambda: self.chosen_service_name("AlphaVantage", alphavantage_button, [macrotrends_button, yahoo_button, nasdaq_button, archive_button]), bg='white', fg='grey12',font=('Calibri',10))
        macrotrends_button = tk.Button(api_panel, text="MacroTrends", command = lambda: self.chosen_service_name("MacroTrends", macrotrends_button, [alphavantage_button, yahoo_button, nasdaq_button, archive_button]), bg='white', fg='grey12',font=('Calibri',10))
        yahoo_button = tk.Button(api_panel, text="Yahoo! Finance", command = lambda: self.chosen_service_name("Yahoo", yahoo_button, [macrotrends_button, alphavantage_button, nasdaq_button, archive_button]), bg='white', fg='grey12',font=('Calibri',10))
        nasdaq_button = tk.Button(api_panel, text="NASDAQ Historical", command = lambda: self.chosen_service_name("Nasdaq", nasdaq_button, [macrotrends_button, alphavantage_button, yahoo_button, archive_button]), bg='white', fg='grey12',font=('Calibri',10))
        archive_button = tk.Button(api_panel, text="Query Archive", command = lambda: self.ask_archive_file_name(), bg='white', fg='grey12',font=('Calibri',10))
        info_button = tk.Button(api_panel, text="Service Information", command = lambda: self.show_service_info(), bg='grey40', fg='white',font=('Calibri',10,'italic'))

        alphavantage_button.grid(row = 0, column = 0, sticky='ewns')
        macrotrends_button.grid(row = 0, column = 1, sticky='ewns')
        yahoo_button.grid(row=0, column=2, sticky='ewns')
        nasdaq_button.grid(row=1, column=0, sticky='ewns')
        archive_button.grid(row=1, column=1, sticky='ewns')
        info_button.grid(row=1, column=2, sticky='ewns')
        api_panel.grid(row = 0, column = 0, sticky='ewns')

    def add_ticker_panel(self):
        """Creates a panel to obtain user input regarding the way they wish to search companies by.
        Composed of buttons for querying by either name or ticker."""
        ticker_question_panel = ttk.LabelFrame(self.root, text="  Search By  ", style = "TLabelframe", labelanchor='n')
        ticker_button = tk.Button(ticker_question_panel, text="Ticker", command=lambda: self.tickers_selected(self.root, name_button, ticker_button), bg='white', fg='grey12',font=('Calibri',10))
        name_button = tk.Button(ticker_question_panel, text="Name", command=lambda: self.names_selected(self.root, name_button, ticker_button), bg='white', fg='grey12',font=('Calibri',10))

        ticker_button.grid(row = 0, column = 0, sticky='ewns')
        name_button.grid(row = 0, column = 1, sticky='ewns')
        ticker_question_panel.grid(row = 2, column = 0, sticky='ewns')

    def add_period_panel(self):
        """Creates a panel to obtain user input regarding the training period to be used and
        the date in the future for which a price prediction is needed.
        Composed of entry fields for the training period start and end dates as well as one for the future date.
        Also contains a button to specify the training frequency to be used."""
        period_panel = ttk.LabelFrame(self.root, text="  Time Period  ", style = "TLabelframe", labelanchor='n')
        date_format_info = ttk.Label(period_panel, text = "Enter dates in the form yyyy-mm-dd.\nNote that the start and end date are inclusive.", style="TLabel")

        #Limiting input dates to a maximum of 10 characters.
        #https://stackoverflow.com/questions/5446553/tkinter-entry-character-limit/39063679
        start_date_question = ttk.Label(period_panel, text = "Start of period:", style="TLabel")
        global start_date_input
        start_date_entry = tk.StringVar()
        start_date_input = ttk.Entry(period_panel, textvariable = start_date_entry)
        start_date_entry.trace("w", lambda *args: self.limit_input(start_date_entry))

        end_date_question = ttk.Label(period_panel, text = "End of period:", style="TLabel")
        global end_date_input
        end_date_entry = tk.StringVar()
        end_date_input = ttk.Entry(period_panel, textvariable = end_date_entry)
        end_date_entry.trace("w", lambda *args: self.limit_input(end_date_entry))

        future_date_question = ttk.Label(period_panel, text = "Date for which price is to be predicted:", style="TLabel")
        global future_date_input
        future_date_entry = tk.StringVar()
        future_date_input = ttk.Entry(period_panel, textvariable = future_date_entry)
        future_date_entry.trace("w", lambda *args: self.limit_input(future_date_entry))

        global daily_button, monthly_button
        daily_button = tk.Button(period_panel, text="Daily", command = lambda: self.chosen_period("d", daily_button, [monthly_button]), bg='white', fg='grey12',font=('Calibri',10))
        monthly_button = tk.Button(period_panel, text="Monthly", command = lambda: self.chosen_period("MS", monthly_button, [daily_button]), bg='white', fg='grey12',font=('Calibri',10))

        date_format_info.grid(row = 0, column = 0, columnspan = 3)
        start_date_question.grid(row = 1, column = 0, columnspan = 2)
        start_date_input.grid(row = 1, column = 2)
        end_date_question.grid(row = 2, column = 0, columnspan = 2)
        end_date_input.grid(row = 2, column = 2)
        future_date_question.grid(row=3, column=0, columnspan=2)
        future_date_input.grid(row=3, column=2)
        daily_button.grid(row=4,column=0)
        monthly_button.grid(row=4, column=1)
        period_panel.grid(row = 1, column = 0, sticky='ewns')

    def chosen_period(self, period, button, other_buttons):
        """Recording the user training frequency period chosen."""
        self.period = period
        button.config(bg='grey12', activebackground='white', foreground = 'white', relief='sunken')
        for btn in other_buttons:
            btn.config(bg='white', activebackground='white', foreground = 'grey12', relief='raised')

    def add_retrieve_button(self):
        """Adding a button to retrieve user inputs and initiate the predictive modeling."""
        retrieve_button = tk.Button(self.root, text="Retrieve Data", command=lambda: self.show_results(), bg='white', fg='grey12',font=('Calibri',10))
        retrieve_button.grid(row = 5, column = 0, sticky='ewns')

    def limit_input(self, entry_text):
        """Limits input into an entry field to 10 characters. Used for limiting date inputs to
        the form yyyy-mm-dd (total of 10 characters)."""
        if len(entry_text.get()) > 10:
            entry_text.set(entry_text.get()[:10])


    def chosen_service_name(self, service_name, button, other_buttons):
        """Records the chosen service name: either the API name or archive. Changes appearance of button
        which has been clicked on."""
        self.service_name = service_name.lower()
        button.config(bg='grey12', activebackground='white', foreground = 'white', relief='sunken')
        for btn in other_buttons:
            btn.config(bg='white', activebackground='white', foreground = 'grey12', relief='raised')

    def ask_archive_file_name(self):
        """Creates pop-up window asking for details about the archive if the Query Archive button is pressed."""
        self.chosen_service_name("Query Archive", archive_button, [macrotrends_button, alphavantage_button, yahoo_button, nasdaq_button])

        frame = tk.Toplevel()
        frame.title("Query Archive")
        frame.config(bg='grey12')

        archive_panel = ttk.LabelFrame(frame, text="  Query Archive  ", style = "TLabelframe", labelanchor='n')
        filename_label = ttk.Label(archive_panel, text="Enter the archive file name: ")
        global filename_in
        filename_in = ttk.Entry(archive_panel)
        column_label = ttk.Label(archive_panel, text="Column name in the archive where\ndates are recorded: ")
        column_in = ttk.Entry(archive_panel)
        enter_button = tk.Button(archive_panel, text = "Enter", command=lambda: self.change_archive_name(filename_in, column_in, frame), bg='white', fg='grey12',font=('Calibri',10))

        filename_label.grid(row=0, column=0, sticky='ewns')
        filename_in.grid(row=0, column=1, sticky='ewns')
        column_label.grid(row=1, column=0, sticky='ewns')
        column_in.grid(row=1, column=1, sticky='ew')
        enter_button.grid(row=2, columnspan=2, sticky='ns')

        archive_panel.grid(row=3, column=0)

    def change_archive_name(self, filename_entrybox, column_in_entrybox, frame):
        """Records the name of the file to be used as the archive. Remains open until a file which
        can be opened is entered."""
        while True:
            try:
                input_filename = filename_entrybox.get()
                f = open(input_filename)
                self.archive_name = input_filename
                self.service_name = "archive"
                self.check_archive_details(column_in_entrybox.get(), frame)
                frame.destroy()
                break
            except FileNotFoundError:
                filename_label = ttk.Label(frame, text="File not found.\nPlease enter the full file path or\nensure it is in the current working directory.")
                filename_label.grid(row=4, column=0)
                print("File not found. Please make sure it is in the current directory.")
                break


    def check_archive_details(self, date_column_in, frame):
        """Checks that the date column name entered is in the archive columns."""
        data = pd.read_csv(self.archive_name)
        if date_column_in in data.columns:
            frame.destroy()
            self.date_column_name = date_column_in
        else:
            notfound_label = ttk.Label(frame, text="Column name not found. Please enter the date column:")
            columns_label = ttk.Label(frame, text=[column for column in data.columns])
            notfound_label.grid(row=3, column=0)
            columns_label.grid(row=4, column=0)


    def tickers_selected(self, root, name_button, ticker_button):
        """Creates a panel to input the list of company tickers to be analysed.
        Composed of an entry box where company tickers are entered, separated by a semi-colon."""
        self.tickers_chosen = True

        ticker_button.config(bg='grey12', activebackground='white', foreground = 'white', relief='sunken')
        name_button.config(bg='white', activebackground='white', foreground = 'grey12', relief='raised')

        ticker_panel = ttk.LabelFrame(self.root, text="  Company Tickers  ", style="TLabelframe", labelanchor='n')
        ticker_label = ttk.Label(ticker_panel, text="Enter the list of company tickers\nseparated by a semi-colon (;).\nIf querying an archive, enter the ticker of the company.")
        global ticker_entry
        ticker_entry = ttk.Entry(ticker_panel)

        ticker_label.grid(row=0, column=0, sticky='ewns')
        ticker_entry.grid(row=1, column=0, sticky='ewns')
        ticker_panel.grid(row=4, column=0)

    def names_selected(self, root, name_button, ticker_button):
        """Creates a panel to input the list of company names to be analysed.
        Composed of an entry box where company names are entered, separated by a semi-colon."""
        self.tickers_chosen = False

        name_button.config(bg='grey12', activebackground='white', foreground = 'white', relief='sunken')
        ticker_button.config(bg='white', activebackground='white', foreground = 'grey12', relief='raised')

        name_panel = ttk.LabelFrame(self.root, text="  Company Names  ", style="TLabelframe", labelanchor='n')
        name_label = ttk.Label(name_panel, text="Enter the list of company names\nseparated by a semi-colon (;).\nIf querying an archive, enter the name of the company.")
        global name_entry
        name_entry = ttk.Entry(name_panel)

        name_label.grid(row=0, column=0, sticky='ewns')
        name_entry.grid(row=1, column=0, sticky='ewns')
        name_panel.grid(row=4, column=0, sticky='ewns', fill=tk.BOTH)

    def date_selected(self, date, frame, start = False, end = False):
        """Recording the start and end dates selected."""
        if start == True and end == False:
            self.start_date = date
        elif start == False and end == True:
            self.end_date = date
        elif start == True and end == True:
            self.start_date, self.end_date = date

        #Destroys the frame once valid start and end dates are obtained.
        if self.start_date != False and self.end_date != False:
            frame.destroy()


    def show_service_info(self):
        """Creates a pop-up window with information about the API services available."""
        frame = tk.Toplevel()
        frame.title("Service Information")
        frame.config(bg='grey12')
        descriptions = {"AlphaVantage": "Access to the last 100 days of trading information.",
                        "MacroTrends": "Can provide information for decades of historical data for companies,\nin some cases over 50 years' worth of share prices.\nThe timespan over which data is provided is longer than any other API.",
                        "Yahoo! Finance": "Data from Yahoo! Finance API, which has been discontinued by the company.\nData from over 10 years is available in some cases.",
                        "NASDAQ Historical": "Access to up to 10 years of historical data\nfor companies trading on the NASDAQ index.",
                        "Query Archive" : "Search through a downloaded file and analyse\nthe stock price trends for a single company."}
        labels = [ttk.Label(frame, text = service) for service in list(descriptions.keys())]
        info = [ttk.Label(frame, text = description) for description in list(descriptions.values())]
        close_button = tk.Button(frame, text = "Close", command=lambda: frame.destroy(), bg='white', fg='grey12',font=('Calibri',10))

        for i in range(len(labels)):
            labels[i].grid(row=i, column=0, padx=10, sticky='ewns')
            info[i].grid(row=i, column=1, sticky='ewns')
        close_button.grid(row=5, columnspan=2, sticky='ns')

    def show_date_options_frame(self, unavailable_date, options, start = False, end = False, multiple_dates = False):
        """Create a pop-up window with possible date options if one of the entered dates is not available."""
        frame = tk.Toplevel(self.root)
        frame.title("Invalid Dates")
        frame.config(bg='grey12')
        #If only one date is invalid:
        if multiple_dates == False:
            options_label = ttk.Label(frame, text="Unfortunately, no data is available for the date {}.\nThe closest dates are: ".format(unavailable_date)).pack()
            option1_button = tk.Button(frame, text=self.option_dates[0], command=lambda: self.date_selected(self.option_dates[0], frame, start, end), bg='white', fg='grey12',font=('Calibri',10)).pack()
            option2_button = tk.Button(frame, text=self.option_dates[1], command=lambda: self.date_selected(self.option_dates[1], frame, start, end), bg='white', fg='grey12',font=('Calibri',10)).pack()
            options_ask_to_select_label = ttk.Label(frame, text="Please click one of the available dates.").pack()

        #If both dates are invalid:
        else:
            options_label = ttk.Label(frame, text="Unfortunately, no data is available for either of the dates {} or {}.\nThe closest dates for which data is available are: ".format(unavailable_date[0], unavailable_date[1]))

            start_label = ttk.Label(frame, text="Start Date")
            start_option1_button = tk.Button(frame, text=self.option_dates[0][0], command=lambda: self.date_selected((self.option_dates[0][0], self.end_date), frame, start=True, end=True), bg='white', fg='grey12',font=('Calibri',10))
            start_option2_button = tk.Button(frame, text=self.option_dates[0][1], command=lambda: self.date_selected((self.option_dates[0][1], self.end_date), frame, start=True, end=True), bg='white', fg='grey12',font=('Calibri',10))

            end_label = ttk.Label(frame, text="End Date")
            end_option1_button = tk.Button(frame, text=self.option_dates[1][0], command=lambda: self.date_selected((self.start_date, self.option_dates[1][0]), frame, start=True, end=True), bg='white', fg='grey12',font=('Calibri',10))
            end_option2_button = tk.Button(frame, text=self.option_dates[1][1], command=lambda: self.date_selected((self.start_date, self.option_dates[1][1]), frame, start=True, end=True), bg='white', fg='grey12',font=('Calibri',10))

            options_ask_to_select_label = ttk.Label(frame, text="Please click one of the available dates.")

            options_label.grid(row=0, column=0, columnspan=2)
            start_label.grid(row=1, column=0)
            end_label.grid(row=1, column=1)
            start_option1_button.grid(row=2, column=0)
            start_option2_button.grid(row=3, column=0)
            end_option1_button.grid(row=2, column=1)
            end_option2_button.grid(row=3, column=1)
            options_ask_to_select_label.grid(row=4, column=0, columnspan=2)
        #Wait for the user to select an option date.
        frame.grab_set()
        self.root.wait_window(frame)

    def parse_companies(self):
        """Reads the list of tickers entered. If names are entered, the names are split
        and the associated tickers are found."""
        if self.tickers_chosen == True:
            self.ticker_list = ticker_entry.get().upper().split(";")
        else:
            self.name_list = name_entry.get().lower().split(";")
            self.ticker_list = [ticker for ticker in search_for_tickers(self.name_list)]

    def read_inputs(self):
        """Read the user inputs in the MenuWindow object."""
        self.start_date = start_date_input.get()
        self.end_date = end_date_input.get()
        self.future_date = future_date_input.get()
        self.parse_companies()


    # def yahoo_check_dates(self, data, start_date_str, end_date_str, multiple_dates = False):
    #     #Find nearest dates to those entered., depending on whether or not the data is in the
    #     #Yahoo! Finance format or not.
    #     dates = data.index.values
    #     if multiple_dates == False:
    #         self.option_dates = find_nearest_date(dates, start_date_str, end_date_str, True)[2]
    #     else:
    #         self.option_dates = find_nearest_date(dates, start_date_str, end_date_str, True)[2:]
    #     print("Option dates:",self.option_dates)

    def ask_for_date_selection(self, data, start_date_valid = False, end_date_valid = False):
        """Reads user input dates. Asks the user to select an available date if data is unavailable."""
        start_date_str = start_date_input.get()
        if start_date_str == "":
            start_date_str = self.start_date
        end_date_str = end_date_input.get()

        if start_date_valid == False and end_date_valid != False:
            # self.yahoo_check_dates(data, start_date_str, end_date_str)
            #Generate a pop-up window asking user to select one of the nearest dates.
            self.show_date_options_frame(start_date_str, self.option_dates, start = True)

        elif end_date_valid == False and start_date_valid != False:
            # self.yahoo_check_dates(data, start_date_str, end_date_str)
            self.show_date_options_frame(end_date_str, self.option_dates, end = True)

        elif start_date_valid == False and end_date_valid == False:
            # self.yahoo_check_dates(data, start_date_str, end_date_str, True)
            self.show_date_options_frame((start_date_str, end_date_str), self.option_dates, multiple_dates = True)

    def notify_of_data_limit(self, date, exception):
        """Creates a pop-up window notifying the user that data for a particular company does not
        extend as far back as desired."""
        frame = tk.Toplevel(self.root)
        frame.title("Data Unavailable")
        frame.config(bg='grey12')

        label = ttk.Label(frame, text="Unfortunately, no data is available for " + exception.ticker + " for the date {}.\nData only exists from the date {} onwards.\nBe advised that the data is only shown from this date.".format(self.start_date, date)).pack()
        frame.grab_set()

    def show_descriptive_stats_frame(self, stats_frame):
        """Creates a pop-up window to show descriptive statistics of company stocks."""
        frame = tk.Toplevel(self.root)
        frame.title("Descriptive Statistics Summary")
        frame.config(bg='white')
        i = 1
        j = 1
        #Getting the statistics for each company.
        statistic_names = [stat_name for stat_name in list(stats_frame.index)]
        statistic_values = [[np.round(stat,3) for stat in stats_frame[self.ticker_list[i]]] for i in range(len(self.ticker_list))]

        #Making labels for each statistic and assigning labels for values of each statistic.
        labels = [ttk.Label(frame, text=statistic) for statistic in statistic_names]
        stats_list = [[ttk.Label(frame, text=statistic) for statistic in statistic_values[i]] for i in range(len(self.ticker_list))]

        #Setting layout of pop-up frame.
        if self.tickers_chosen == True:
            labels.insert(0, ttk.Label(frame, text="Ticker"))
            tickers = [ttk.Label(frame, text=ticker) for ticker in self.ticker_list]

        else:
            labels.insert(0, ttk.Label(frame, text="Company Name"))
            tickers = [ttk.Label(frame, text=name.title()) for name in self.name_list]

        for ticker in tickers:
            ticker.grid(row=0, column=i, pady = 1, sticky = 'ewns')
            i += 1

        i = 0
        for label in labels:
            if i != 0:
                label.grid(row=i, column=0, padx = 2, sticky = 'ewns')
            else:
                label.grid(row=i, column=0, padx = 1, pady = 1, sticky = 'ewns')
            i += 1

        i = 1
        for stats in stats_list:
            for stat in stats:
                stat.grid(row=i, column=j, padx = 1, sticky = 'ewns')
                i += 1
            i = 1
            j += 1

        frame.grab_set()


    def retrieve_valid_data(self):
        """Reads and validates user inputs in the MenuWindow fields."""
        self.read_inputs()

        #If Query Archive is not chosen, data is drawn from the API.
        if self.service_name != "archive":
            data = connect_to_api(self.service_name, self.ticker_list[0], "NO7SX7BKV0TRLHAM", self.start_date, self.end_date, True)[0]
            if self.start_date == "":
                self.start_date = data.index[-1]

            self.start_date, self.end_date = check_dates(data, self.start_date, self.end_date, True)[0:2]
            if self.start_date == False or self.end_date == False:
                self.ask_for_date_selection(data, self.start_date, self.end_date)


    def make_datasets_and_stats_frame(self):
        """Creates the data to be used as model inputs. Plots the raw time series if Query Archive is chosen
        or only one company is queried.
        Where multiple companies are queried, if data does not extend as far back for one company as it does
        for the first company entered, an exception is raised."""
        self.retrieve_valid_data()

        if self.service_name == "archive":
            self.stats_frame, data, ticker, reverse_data, new_start, new_end = make_single_frame(self.service_name, self.ticker_list[0], self.start_date, self.end_date, gui = True, filename = self.archive_name, date_column_name = self.date_column_name)
            plot_raw_time_series(data, self.ticker_list[0])
            self.data_sets = [data]

        else:
            if len(self.ticker_list) == 1:
                self.stats_frame, data, ticker, reverse_data, new_start, new_end = make_single_frame(self.service_name, self.ticker_list[0], self.start_date, self.end_date, gui = True)
                self.ticker_list = [ticker]
                self.data_sets = [data]
                plot_raw_time_series(self.data_sets[0], self.ticker_list[0])

            else:
                try:
                    self.stats_frame, self.data_sets, self.ticker_list, unavailable_index_date = make_full_frame(self.service_name, self.ticker_list, self.start_date, self.end_date, gui = True)

                    if len(unavailable_index_date) != 0:
                        exceptions = MultiDataUnavailableException()
                        for index, date in unavailable_index_date:
                            exceptions.add_exception(DataUnavailableException(self.ticker_list[index], self.start_date), self.ticker_list[index])
                        raise exceptions

                except MultiDataUnavailableException as exc:
                    for e, (index, date) in zip(exc.exceptions, unavailable_index_date):
                        print("Exception occured.")
                        print(e.message)
                        self.notify_of_data_limit(date, e)


    def plot_data(self, data_sets, tickers, future_date, period, steps):
        """Creates the plots for the linear regression and ARIMA models.
        Creates a pop-up window with the descriptive statistics of all entered companies."""
        if self.service_name == "alphavantage":
            period = "d"

        linear_plot, rmse, r2, linear_min, linear_max = plot_linear_regression(data_sets, tickers, future_date, period, steps)
        arima_plot, rmse_list, r2_list, linear_min, linear_max, arima_min, arima_max  = plot_time_series_forecasts(data_sets, tickers, future_date, period, steps)

        #plots, rmse_list, r2_list, linear_min, linear_max, arima_min, arima_max = plot_data_text_interface(service_name, data_sets, tickers, period_choice, 20, future_date)
        model_result = pd.DataFrame([rmse_list, r2_list, linear_min, linear_max, arima_min, arima_max],
                                    index = ["RMSE", "R^2", "Linear Regression: Minimum","Linear Regression: Maximum","ARIMA: Minimum","ARIMA: Maximum",],
                                    columns = tickers)
        self.stats_frame = self.stats_frame.append(model_result)

        self.show_descriptive_stats_frame(self.stats_frame)

        if len(data_sets) == 1:
            return (linear_plot, arima_plot), rmse, r2
        else:
            return (linear_plot, arima_plot), rmse_list, r2_list

    def show_results(self):
        """Show the plots created."""
        #Could not quite manage to get loading window to run properly.
        loading_window = LoadingScreen(self.root)
        show_loading = threading.Thread(target = loading_window.check_if_finished, daemon=True)
        show_loading.start()

        #loading_window.update()
        # loading_window.update_loading_symbol()
        # loading_window.update()

        self.make_datasets_and_stats_frame()
        print("Making plots...")
        plots, rmse_list, r2_list = self.plot_data(self.data_sets, self.ticker_list, self.future_date, self.period, 24)

        for plot in plots:
            plot.show()

        # loading_window.finished = True
        # loading_window.check_if_finished()


#Class of TopLevel which is to be used as a loading screen. Does not quite work.
class LoadingScreen(tk.Toplevel):

    def __init__(self, menu):
        tk.Toplevel.__init__(self, menu)
        self.title("Loading...")
        self.config(bg='white')
        self.geometry("200x200")

        self.finished = False

        self.loading_label_text = tk.StringVar()
        self.loading_label = tk.Label(self, textvariable = self.loading_label_text)
        self.loading_label.pack()
        self.update()

    def update_loading_symbol(self):
        display = "."
        self.loading_label_text.set(display)

        start_time = time.time()

        time.sleep(2)
        self.loading_label_text.set("Changed")

        #Trying to print in sequence: '.', '..', '...', '....', changing every 5 seconds.
        while self.finished == False:
            elapsed = time.time() - start_time
            if elapsed % 5 < 1e-2:
                print(elapsed)
                if len(display) < 4:
                    display += "."
                    print("DISPLAY:",display)
                    self.loading_label_text.set(display)
                    self.update()
                else:
                    display = "."
                    self.loading_label_text.set(display)
                    self.update()
                continue
            self.loading_label_text.set(display)
            self.update()
            self.check_if_finished()


    def check_if_finished(self):
        self.update_loading_symbol()
        self.update()
        if self.finished == True:
            self.destroy()
