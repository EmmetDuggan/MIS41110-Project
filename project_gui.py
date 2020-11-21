from project_io import connect_to_api, search_for_tickers, check_dates
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
        self.root = tk.Tk()
        self.root.wm_title("Stocks GUI")

        self.s = ttk.Style()
        self.s.configure("TButton", font=("Calibri", 10), foreground = 'grey12', background = 'white')
        self.s.configure("TLabel", font=("Calibri",10), foreground = 'white', weight="bold", background = 'grey12')
        self.s.configure("TLabelframe", background = 'grey12', labelanchor='n')


        self.add_api_panel()
        self.add_ticker_panel()
        self.add_period_panel()
        self.add_retrieve_button()


        self.root.config(bg='grey12')
        self.root.geometry("600x600")
        self.root.mainloop()

        self.stats_frame = pd.DataFrame()
        self.data_sets = []
        self.date_column_name = ""
        self.tickers_chosen = False
        self.ticker_list = []
        self.name_list = []
        self.service_name = ""
        self.archive_name = ""
        self.start_date = ""
        self.end_date = ""
        self.option_dates = []

    def add_api_panel(self):
        api_panel = ttk.LabelFrame(self.root, text="  Service Name  ", style = "TLabelframe", labelanchor='n')
        alphavantage_button = tk.Button(api_panel, text="AlphaVantage", command = lambda: self.chosen_service_name("AlphaVantage", alphavantage_button, [macrotrends_button, yahoo_button, nasdaq_button, archive_button]), bg='white', fg='grey12',font=('Calibri',10))
        macrotrends_button = tk.Button(api_panel, text="MacroTrends", command = lambda: self.chosen_service_name("MacroTrends", macrotrends_button, [alphavantage_button, yahoo_button, nasdaq_button, archive_button]), bg='white', fg='grey12',font=('Calibri',10))
        yahoo_button = tk.Button(api_panel, text="Yahoo! Finance", command = lambda: self.chosen_service_name("Yahoo", yahoo_button, [macrotrends_button, alphavantage_button, nasdaq_button, archive_button]), bg='white', fg='grey12',font=('Calibri',10))
        nasdaq_button = tk.Button(api_panel, text="NASDAQ Historical", command = lambda: self.chosen_service_name("Nasdaq", nasdaq_button, [macrotrends_button, alphavantage_button, yahoo_button, archive_button]), bg='white', fg='grey12',font=('Calibri',10))
        archive_button = tk.Button(api_panel, text="Query Archive", command = lambda: self.ask_archive_file_name(), bg='white', fg='grey12',font=('Calibri',10))
        info_button = tk.Button(api_panel, text="Service Information", command = lambda: self.show_service_info(), bg='grey40', fg='grey12',font=('Calibri',10))

        alphavantage_button.grid(row = 0, column = 0)
        macrotrends_button.grid(row = 0, column = 1)
        yahoo_button.grid(row=1, column=0, sticky='ewns')
        nasdaq_button.grid(row=1, column=1, sticky='ewns')
        archive_button.grid(row=1, column=2, sticky='ewns')
        info_button.grid(row=2, columnspan=2)
        api_panel.grid(row = 0, column = 0, sticky='ewns')

    def add_ticker_panel(self):
        ticker_question_panel = ttk.LabelFrame(self.root, text="  Search By  ", style = "TLabelframe", labelanchor='n')
        ticker_button = tk.Button(ticker_question_panel, text="Ticker", command=lambda: self.tickers_selected(self.root, name_button, ticker_button), bg='white', fg='grey12',font=('Calibri',10))
        name_button = tk.Button(ticker_question_panel, text="Name", command=lambda: self.names_selected(self.root, name_button, ticker_button), bg='white', fg='grey12',font=('Calibri',10))


        ticker_button.grid(row = 0, column = 0, sticky='ewns')
        name_button.grid(row = 0, column = 1, sticky='ewns')
        ticker_question_panel.place(x=230, y=20, anchor='w')

    def add_period_panel(self):
        period_panel = ttk.LabelFrame(self.root, text="  Time Period  ", style = "TLabelframe", labelanchor='n')
        date_format_info = ttk.Label(period_panel, text = "Enter dates in the form yyyy-mm-dd.\nNote that the end date is not inclusive.", style="TLabel")

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

        date_format_info.grid(row = 0, column = 0, sticky='ewns', columnspan = 2)
        start_date_question.grid(row = 1, column = 0, sticky='ewns')
        start_date_input.grid(row = 1, column = 1, sticky='ewns')
        end_date_question.grid(row = 2, column = 0, sticky='ewns')
        end_date_input.grid(row = 2, column = 1, sticky='ewns')
        period_panel.grid(row = 2, column = 0, sticky='ewns')

    def add_retrieve_button(self):
        retrieve_button = tk.Button(self.root, text="Retrieve Data", command=lambda: self.show_results(), bg='white', fg='grey12',font=('Calibri',10))
        retrieve_button.grid(row = 3, column = 0, sticky='ewns')

    def limit_input(self, entry_text):
        if len(entry_text.get()) > 10:
            entry_text.set(entry_text.get()[:10])




    def chosen_service_name(self, service_name, button, other_buttons):
        #Setting the global variable to the chosen service name.
        self.service_name = service_name.lower()
        button.config(bg='grey12', activebackground='white', foreground = 'white', relief='sunken')
        for btn in other_buttons:
            btn.config(bg='white', activebackground='white', foreground = 'grey12', relief='raised')

    def ask_archive_file_name(self):
        self.chosen_service_name("Query Archive", nasdaq_button, [macrotrends_button, alphavantage_button, yahoo_button, nasdaq_button])

        frame = tk.Toplevel()
        frame.title("Query Archive")
        frame.config(bg='grey12')

        archive_panel = ttk.LabelFrame(frame, text="  Query Archive  ", style = "TLabelframe", labelanchor='n')
        filename_label = ttk.Label(archive_panel, text="Enter the archive file name: ")
        filename_in = ttk.Entry(archive_panel)
        enter_button = tk.Button(frame, text = "Enter", command=lambda: frame.destroy(), bg='white', fg='grey12',font=('Calibri',10))

        filename_label.grid(row=0, column=0, sticky='ewns')
        filename_in.grid(row=1, column=0, sticky='ewns')
        #archive_panel.grid(row=3, column=0)

    def change_archive_name(self, entrybox, frame):
        self.archive_name = entrybox.get()
        while True:
            try:
                f = open(self.archive_name)
                frame.destroy()
            except FileNotFoundError:
                print("File not found. Please make sure it is in the current directory.")

    def tickers_selected(self, root, name_button, ticker_button):
        #Panel to input the list of company tickers to be analysed.
        self.tickers_chosen = True

        ticker_button.config(bg='grey12', activebackground='white', foreground = 'white', relief='sunken')
        name_button.config(bg='white', activebackground='white', foreground = 'grey12', relief='raised')

        ticker_panel = ttk.LabelFrame(self.root, text="  Company Tickers  ", style="TLabelframe", labelanchor='n')
        ticker_label = ttk.Label(ticker_panel, text="Enter the list of company tickers separated by a semi-colon (;).")
        global ticker_entry
        ticker_entry = ttk.Entry(ticker_panel)

        ticker_label.grid(row=0, column=0, sticky='ewns')
        ticker_entry.grid(row=1, column=0, sticky='ewns')
        ticker_panel.grid(row=2, column=1)

    def names_selected(self, root, name_button, ticker_button):
        #Panel to input the list of company names to be analysed.
        self.tickers_chosen = False

        name_button.config(bg='grey12', activebackground='white', foreground = 'white', relief='sunken')
        ticker_button.config(bg='white', activebackground='white', foreground = 'grey12', relief='raised')

        name_panel = ttk.LabelFrame(self.root, text="  Company Names  ", style="TLabelframe", labelanchor='n')
        name_label = ttk.Label(name_panel, text="Enter the list of company names separated by a semi-colon (;).")
        global name_entry
        name_entry = ttk.Entry(name_panel)

        name_label.grid(row=0, column=0, sticky='ewns')
        name_entry.grid(row=1, column=0, sticky='ewns')
        name_panel.grid(row=2, column=1, sticky='ewns')

    def date_selected(self, date, frame, start = False, end = False):
        #Setting the global variables for the start and end dates to those selected.
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
        frame = tk.Toplevel()
        frame.title("Service Information")
        frame.config(bg='grey12')
        descriptions = {"AlphaVantage": "Access to the last 100 days\nof trading information.",
                        "MacroTrends": "macrotrends info",
                        "Yahoo! Finance": "Data from Yahoo! Finance API, which has been discontinued by the company.\nRecords begin from",
                        "NASDAQ Historical": "Access to up to 10 years of historical data\nfor companies trading on the NASDAQ index."}
        labels = [ttk.Label(frame, text = service) for service in list(descriptions.keys())]
        info = [ttk.Label(frame, text = description) for description in list(descriptions.values())]
        close_button = tk.Button(frame, text = "Close", command=lambda: frame.destroy(), bg='white', fg='grey12',font=('Calibri',10))

        for i in range(len(labels)):
            labels[i].grid(row=i, column=0, padx=10, sticky='ewns')
            info[i].grid(row=i, column=1, sticky='ewns')
        close_button.grid(row=4, sticky='n')

    def show_date_options_frame(self, unavailable_date, options, start = False, end = False, multiple_dates = False):
        #Create a pop-up frame with possible date options if one of the entered dates is not available.
        frame = tk.Toplevel(self.root)
        frame.title("Invalid Dates")
        frame.config(bg='grey12')
        if multiple_dates == False:
            options_label = ttk.Label(frame, text="Unfortunately, no data is available for the date {}.\nThe closest dates are: ".format(unavailable_date)).pack()
            option1_button = tk.Button(frame, text=self.option_dates[0], command=lambda: self.date_selected(self.option_dates[0], frame, start, end), bg='white', fg='grey12',font=('Calibri',10)).pack()
            option2_button = tk.Button(frame, text=self.option_dates[1], command=lambda: self.date_selected(self.option_dates[1], frame, start, end), bg='white', fg='grey12',font=('Calibri',10)).pack()
            options_ask_to_select_label = ttk.Label(frame, text="Please click one of the available dates.").pack()

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
        frame.grab_set()
        #self.root.wait_window(frame)

    def read_inputs(self):
        #Read the user inputs in the menu frame.

        self.start_date = start_date_input.get()
        self.end_date = end_date_input.get()
        if self.tickers_chosen == True:
            self.ticker_list = ticker_entry.get().upper().split(";")
        else:
            self.name_list = name_entry.get().lower().split(";")
            self.ticker_list = [ticker for ticker in search_for_tickers(self.name_list)]

    def yahoo_check_dates(self, data, date_column_name, start_date_str, end_date_str, multiple_dates = False):
        #Find nearest dates to those entered., depending on whether or not the data is in the
        #Yahoo! Finance format or not.
        if date_column_name != "yahoo":
            self.option_dates = find_nearest_date(data[date_column_name], start_date_str, end_date_str, True)[2]
        else:
            dates = [datetime.datetime.strftime(date, '%Y-%m-%d') for date in data.index]
            if multiple_dates == False:
                self.option_dates = find_nearest_date(dates, start_date_str, end_date_str, True)[2]
            else:
                self.option_dates = find_nearest_date(dates, start_date_str, end_date_str, True)[2:]
            print("Option dates:",self.option_dates)

    def ask_for_date_selection(self, data, date_column_name, start_date_valid = False, end_date_valid = False):
        #Read user input dates.
        start_date_str = start_date_input.get()
        if start_date_str == "":
            start_date_str = self.start_date
            print(start_date_str)
        end_date_str = end_date_input.get()
        if start_date_valid == False and end_date_valid != False:
            self.yahoo_check_dates(data, date_column_name, start_date_str, end_date_str)
            #Generate a pop-up window asking user to select one of the nearest dates.
            self.show_date_options_frame(start_date_str, self.option_dates, start = True)

        elif end_date_valid == False and start_date_valid != False:
            self.yahoo_check_dates(data, date_column_name, start_date_str, end_date_str)
            self.show_date_options_frame(end_date_str, self.option_dates, end = True)

        elif start_date_valid == False and end_date_valid == False:
            self.yahoo_check_dates(data, date_column_name, start_date_str, end_date_str, True)
            self.show_date_options_frame((start_date_str, end_date_str), self.option_dates, multiple_dates = True)

    def notify_of_data_limit(self, date, exception):
        #Create a pop-up frame with possible date options if one of the entered dates is not available.
        frame = tk.Toplevel(self.root)
        frame.title("Data Unavailable")
        frame.config(bg='grey12')

        label = ttk.Label(frame, text="Unfortunately, no data is available for " + exception.ticker + " for the date {}.\nData only exists from the date {} onwards.\nBe advised that the data is only shown from this date.".format(self.start_date, date)).pack()
        frame.grab_set()

    def show_descriptive_stats_frame(self, stats_frame):
        #Generate pop-up window to show descriptive statistics of company stocks.
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
        self.root.wait_window(frame)


    def retrieve_valid_data(self):
        #Read the user input fields.
        self.read_inputs()

        if self.service_name == "yahoo":
            data = connect_to_api("yahoo", self.ticker_list[0], "NO7SX7BKV0TRLHAM", self.start_date, self.end_date, True)
            self.date_column_name = "yahoo"

            if self.start_date == "":
                self.start_date = datetime.datetime.strftime(pd.to_datetime(data.index[0]), '%Y-%m-%d')
            self.start_date, self.end_date = check_dates(data, "yahoo", self.start_date, self.end_date, True)

            if self.start_date == False or self.end_date == False:
                self.ask_for_date_selection(data, "yahoo", self.start_date, self.end_date)

        else:
            data, self.date_column_name = connect_to_api(self.service_name, self.ticker_list[0], "NO7SX7BKV0TRLHAM", self.start_date, self.end_date, True)[0:2]

            if self.start_date == "":
                self.start_date = data[date_column_name].iloc[-1::].item()

            self.start_date, self.end_date = check_dates(data, self.date_column_name, self.start_date, self.end_date, True)
            if self.start_date == False or self.end_date == False:
                self.ask_for_date_selection(data, self.date_column_name, self.start_date, self.end_date)


    def make_datasets_and_stats_frame(self):

        self.retrieve_valid_data()

        if len(self.ticker_list) == 1:
            self.stats_frame, data, self.date_column_name, reverse_data, new_start, new_end = make_single_frame(self.service_name, self.ticker_list[0], self.start_date, self.end_date, gui = True)
            plot_raw_time_series(data, self.ticker_list[0], self.date_column_name)

        else:
            try:
                self.stats_frame, self.data_sets, self.tickers_list, unavailable_index_date = make_full_frame(self.service_name, self.ticker_list, self.start_date, self.end_date, gui = True)
                print("unavailable_index_date: ",unavailable_index_date)
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

            # return stats_frame, data_sets, tickers
            #self.plot_data(self.data_sets, self.tickers_list, self.date_column_name, "MS", 24)

    def plot_data(self, data_sets, tickers, date_column_name, period, steps):

        if self.service_name == "alphavantage":
            period = "d"

        self.show_descriptive_stats_frame(self.stats_frame)
        linear_plot = plot_linear_regression(data_sets, tickers, date_column_name, period, steps)
        arima_plot = plot_time_series_forecasts(data_sets, tickers, date_column_name, period, steps)

        return linear_plot, arima_plot

    def show_results(self):

        loading_window = LoadingScreen(self.root)
        show_loading = threading.Thread(target = loading_window.check_if_finished)
        print("Got to here")
        show_loading.start()
        print("Started thread")

        #loading_window.update()
        loading_window.update_loading_symbol()
        # loading_window.update()
        print("Making frames")
        self.make_datasets_and_stats_frame()
        print("Making plots...")
        plots = self.plot_data(self.data_sets, self.tickers_list, self.date_column_name, "MS", 24)
        print("Done making plots")

        loading_window.finished = True
        loading_window.check_if_finished()

        for plot in plots:
            plot.show()







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


        while self.finished == False:
            elapsed = time.time() - start_time
            if elapsed % 10 < 1e-2:
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
        if self.finished == True:
            self.destroy()
