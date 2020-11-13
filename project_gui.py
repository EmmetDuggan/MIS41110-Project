from project_io import connect_to_api, search_for_tickers, check_dates
from project_calendar import find_nearest_date
from project_data_visualisation import plot_single_time_series, plot_multiple_time_series
from project_descriptive_stats import compute_descriptive_stats, make_stats_frame, add_to_frame
from project_frames import make_single_frame, make_full_frame
import datetime
import numpy as np
import tkinter as tk
from tkinter import ttk


class MenuWindow():

    tickers = False
    ticker_list = []
    name_list = []
    service_name = ""
    start_date = ""
    end_date = ""
    option_dates = []


    def __init__(self, master=None):
        self.root = tk.Tk()
        self.root.wm_title("Stocks GUI")

        self.s = ttk.Style()
        self.s.configure("TButton", font=("Calibri", 10), foreground = 'grey8', background = 'ivory')
        self.s.configure("TLabel", font=("Calibri",10), foreground = 'grey75', weight="bold", background = 'black')
        self.s.configure("TLabelframe", background = 'black', labelanchor='n')


        self.add_api_panel()
        self.add_ticker_panel()
        self.add_period_panel()
        self.add_retrieve_button()


        self.root.config(bg='black')
        self.root.geometry("600x600")
        self.root.mainloop()

    def add_api_panel(self):
        api_panel = ttk.LabelFrame(self.root, text="Service Name", style = "TLabelframe", labelanchor='n')
        alphavantage_button = tk.Button(api_panel, text="AlphaVantage", command = lambda: self.chosen_service_name("AlphaVantage", alphavantage_button, [macrotrends_button, yahoo_button]), bg='ivory', fg='grey8',font=('Calibri',10))
        macrotrends_button = tk.Button(api_panel, text="MacroTrends", command = lambda: self.chosen_service_name("MacroTrends", macrotrends_button, [alphavantage_button, yahoo_button]), bg='ivory', fg='grey8',font=('Calibri',10))
        yahoo_button = tk.Button(api_panel, text="Yahoo! Finance", command = lambda: self.chosen_service_name("Yahoo", yahoo_button, [macrotrends_button, alphavantage_button]), bg='ivory', fg='grey8',font=('Calibri',10))

        alphavantage_button.grid(row = 0, column = 0, sticky='ewns')
        macrotrends_button.grid(row = 0, column = 1, sticky='ewns')
        yahoo_button.grid(row=0, column=2, sticky='ewns')
        api_panel.grid(row = 0, column = 0, sticky='ewns')

    def add_ticker_panel(self):
        ticker_question_panel = ttk.LabelFrame(self.root, text="Search By", style = "TLabelframe", labelanchor='n')
        ticker_button = tk.Button(ticker_question_panel, text="Ticker", command=lambda: self.tickers_selected(self.root, name_button, ticker_button), bg='ivory', fg='grey8',font=('Calibri',10))
        name_button = tk.Button(ticker_question_panel, text="Name", command=lambda: self.names_selected(self.root, name_button, ticker_button), bg='ivory', fg='grey8',font=('Calibri',10))


        ticker_button.grid(row = 0, column = 0, sticky='ewns')
        name_button.grid(row = 0, column = 1, sticky='ewns')
        ticker_question_panel.place(x=230, y=20, anchor='w')

    def add_period_panel(self):
        period_panel = ttk.LabelFrame(self.root, text="Time Period", style = "TLabelframe", labelanchor='n')
        date_format_info = ttk.Label(period_panel, text = "Enter dates in the form yyyy-mm-dd.\nNote that the end date is not inclusive.", style="TLabel")
        start_date_question = ttk.Label(period_panel, text = "Start of period:", style="TLabel")
        global start_date_input
        start_date_input = ttk.Entry(period_panel)
        end_date_question = ttk.Label(period_panel, text = "End of period:", style="TLabel")
        global end_date_input
        end_date_input = ttk.Entry(period_panel)


        date_format_info.grid(row = 0, column = 0, sticky='ewns', columnspan = 2)
        start_date_question.grid(row = 1, column = 0, sticky='ewns')
        start_date_input.grid(row = 1, column = 1, sticky='ewns')
        end_date_question.grid(row = 2, column = 0, sticky='ewns')
        end_date_input.grid(row = 2, column = 1, sticky='ewns')
        period_panel.grid(row = 2, column = 0, sticky='ewns')

    def add_retrieve_button(self):
        retrieve_button = tk.Button(self.root, text="Retrieve Data", command=lambda: self.retrieve_data(), bg='ivory', fg='grey8',font=('Calibri',10))
        retrieve_button.grid(row = 3, column = 0, sticky='ewns')

    def chosen_service_name(self, service_name, button, other_buttons):
        #Setting the global variable to the chosen service name.
        self.service_name = service_name.lower()
        button.config(bg='black', activebackground='ivory', foreground = 'grey75', relief='sunken')
        for btn in other_buttons:
            btn.config(bg='ivory', activebackground='ivory', foreground = 'grey8', relief='raised')


    def tickers_selected(self, root, name_button, ticker_button):
        #Panel to input the list of company tickers to be analysed.
        self.tickers = True

        ticker_button.config(bg='black', activebackground='ivory', foreground = 'grey75', relief='sunken')
        name_button.config(bg='ivory', activebackground='ivory', foreground = 'grey8', relief='raised')

        ticker_panel = ttk.LabelFrame(self.root, text="Company Tickers", style="TLabelframe", labelanchor='n')
        ticker_label = ttk.Label(ticker_panel, text="Enter the list of company tickers separated by a semi-colon (;).")
        global ticker_entry
        ticker_entry = ttk.Entry(ticker_panel)

        ticker_label.grid(row=0, column=0, sticky='ewns')
        ticker_entry.grid(row=1, column=0, sticky='ewns')
        ticker_panel.grid(row=2, column=1)

    def names_selected(self, root, name_button, ticker_button):
        #Panel to input the list of company names to be analysed.
        self.tickers = False

        name_button.config(bg='black', activebackground='ivory', foreground = 'grey75', relief='sunken')
        ticker_button.config(bg='ivory', activebackground='ivory', foreground = 'grey8', relief='raised')

        name_panel = ttk.LabelFrame(self.root, text="Company Names", style="TLabelframe", labelanchor='n')
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


    def show_date_options_frame(self, unavailable_date, options, start = False, end = False, multiple_dates = False):
        #Create a pop-up frame with possible date options if one of the entered dates is not available.
        frame = tk.Toplevel(self.root)
        frame.title("Invalid Dates")
        frame.config(bg='black')
        if multiple_dates == False:
            options_label = ttk.Label(frame, text="Unfortunately, no data is available for the date {}.\nThe closest dates are: ".format(unavailable_date)).pack()
            option1_button = tk.Button(frame, text=self.option_dates[0], command=lambda: self.date_selected(self.option_dates[0], frame, start, end), bg='ivory', fg='grey8',font=('Calibri',10)).pack()
            option2_button = tk.Button(frame, text=self.option_dates[1], command=lambda: self.date_selected(self.option_dates[1], frame, start, end), bg='ivory', fg='grey8',font=('Calibri',10)).pack()
            options_ask_to_select_label = ttk.Label(frame, text="Please click one of the available dates.").pack()

        else:
            options_label = ttk.Label(frame, text="Unfortunately, no data is available for either of the dates {} or {}.\nThe closest dates are: ".format(unavailable_date[0], unavailable_date[1]))

            start_label = ttk.Label(frame, text="Start Date")
            start_option1_button = tk.Button(frame, text=self.option_dates[0][0], command=lambda: self.date_selected((self.option_dates[0][0], self.end_date), frame, start=True, end=True), bg='ivory', fg='grey8',font=('Calibri',10))
            start_option2_button = tk.Button(frame, text=self.option_dates[0][1], command=lambda: self.date_selected((self.option_dates[0][1], self.end_date), frame, start=True, end=True), bg='ivory', fg='grey8',font=('Calibri',10))

            end_label = ttk.Label(frame, text="End Date")
            end_option1_button = tk.Button(frame, text=self.option_dates[1][0], command=lambda: self.date_selected((self.start_date, self.option_dates[1][0]), frame, start=True, end=True), bg='ivory', fg='grey8',font=('Calibri',10))
            end_option2_button = tk.Button(frame, text=self.option_dates[1][1], command=lambda: self.date_selected((self.start_date, self.option_dates[1][1]), frame, start=True, end=True), bg='ivory', fg='grey8',font=('Calibri',10))

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
        self.root.wait_window(frame)

    def read_inputs(self):
        #Read the user inputs in the menu frame.
        self.start_date = start_date_input.get()
        self.end_date = end_date_input.get()
        if self.tickers == True:
            self.ticker_list = ticker_entry.get().split(";")
        else:
            self.name_list = name_entry.get().lower().split(";")
            self.ticker_list = [ticker for ticker in search_for_tickers(self.name_list)]

    def ask_for_date_selection(self, data, date_column_name, start_date_valid = False, end_date_valid = False):
        if start_date_valid == False and end_date_valid != False:
            #Read user input dates.
            start_date_str = start_date_input.get()
            end_date_str = end_date_input.get()
            #Find nearest dates to those entered.
            if date_column_name != "yahoo":
                self.option_dates = find_nearest_date(data[date_column_name], start_date_str, end_date_str, True)[2]
            else:
                dates = [datetime.datetime.strftime(date, '%Y-%m-%d') for date in data.index]
                self.option_dates = find_nearest_date(dates, start_date_str, end_date_str, True)[2]
            #Generate a pop-up window asking user to select one of the nearest dates.
            self.show_date_options_frame(start_date_str, self.option_dates, start = True)

        elif end_date_valid == False and start_date_valid != False:
            start_date_str = start_date_input.get()
            end_date_str = end_date_input.get()
            self.option_dates = find_nearest_date(data[date_column_name], start_date_str, end_date_str, True)[2]
            self.show_date_options_frame(end_date_str, self.option_dates, end = True)

        elif start_date_valid == False and end_date_valid == False:
            start_date_str = start_date_input.get()
            end_date_str = end_date_input.get()
            self.option_dates = find_nearest_date(data[date_column_name], start_date_str, end_date_str, True)[2:]
            self.show_date_options_frame((start_date_str, end_date_str), self.option_dates, multiple_dates = True)

    def show_descriptive_stats_frame(self, stats_frame):
        #Generate pop-up window to show descriptive statistics of company stocks.
        frame = tk.Toplevel(self.root)
        frame.title("Descriptive Statistics Summary")
        frame.config(bg='ivory')
        i = 1
        j = 1
        #Getting the statistics for each company.
        statistic_names = [stat_name for stat_name in list(stats_frame.index)]
        statistic_values = [[np.round(stat,3) for stat in stats_frame[self.ticker_list[i]]] for i in range(len(self.ticker_list))]

        #Making labels for each statistic and assigning labels for values of each statistic.
        labels = [ttk.Label(frame, text=statistic) for statistic in statistic_names]
        stats_list = [[ttk.Label(frame, text=statistic) for statistic in statistic_values[i]] for i in range(len(self.ticker_list))]

        #Setting layout of pop-up frame.
        if self.tickers == True:
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


    def retrieve_data(self):
        #Read the user input fields.
        self.read_inputs()

        if self.service_name == "yahoo":
            data = connect_to_api("yahoo", self.ticker_list[0], "NO7SX7BKV0TRLHAM", self.start_date, self.end_date, True)
            date_column_name = "yahoo"
            self.start_date, self.end_date = check_dates(data, "yahoo", self.start_date, self.end_date, True)
            if self.start_date == False or self.end_date == False:
                self.ask_for_date_selection(data, "yahoo", self.start_date, self.end_date)
        else:
            data, date_column_name = connect_to_api(self.service_name, self.ticker_list[0], "NO7SX7BKV0TRLHAM", self.start_date, self.end_date, True)[0:2]
            self.start_date, self.end_date = check_dates(data, date_column_name, self.start_date, self.end_date, True)
            if self.start_date == False or self.end_date == False:
                self.ask_for_date_selection(data, date_column_name, self.start_date, self.end_date)

        if len(self.ticker_list) == 1:
            stats_frame, data, date_column_name, new_start, new_end = make_single_frame(self.service_name, self.ticker_list[0], self.start_date, self.end_date, gui = True)
            plot_single_time_series(data, self.ticker_list[0], date_column_name)
        else:
            stats_frame, data_sets, tickers = make_full_frame(self.service_name, self.ticker_list, self.start_date, self.end_date, gui = True)
            plot_multiple_time_series(data_sets, tickers, date_column_name)
        self.show_descriptive_stats_frame(stats_frame)


    def clickExitButton(self):
        print("Exiting")
        quit()
