from project_io import connect_to_api, search_for_tickers, check_dates
from project_calendar import get_valid_dates, find_nearest_date
# from project_data_visualisation import plot_single_time_series, plot_multiple_time_series
from project_descriptive_stats import compute_descriptive_stats, make_stats_frame, add_to_frame
from project import make_single_frame
import numpy as np
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont


class MenuWindow():

    tickers = False
    ticker = ""
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
        #api_name_question = ttk.Label(api_panel, text = "Service Name", style="TLabel", anchor=tk.CENTER)
        alphavantage_button = tk.Button(api_panel, text="AlphaVantage", command = lambda: self.chosen_service_name("AlphaVantage"), bg='ivory', fg='grey8',font=('Calibri',10))
        macrotrends_button = tk.Button(api_panel, text="MacroTrends", command = lambda: self.chosen_service_name("MacroTrends"), bg='ivory', fg='grey8',font=('Calibri',10))

        #api_name_question.grid(row = 0,  column = 0, columnspan = 2,padx = 10, pady = 5, sticky='ewns')
        alphavantage_button.grid(row = 0, column = 0, sticky='ewns')
        macrotrends_button.grid(row = 0, column = 1, sticky='ewns')
        api_panel.grid(row = 0, column = 0, sticky='ewns')

    def add_ticker_panel(self):
        ticker_question_panel = ttk.LabelFrame(self.root, text="Search By", style = "TLabelframe", labelanchor='n')
        #ticker_name_question = ttk.Label(ticker_question_panel, text = "Search By", style="TLabel", anchor=tk.CENTER)
        ticker_button = tk.Button(ticker_question_panel, text="Ticker", command=lambda: self.tickers_selected(self.root), bg='ivory', fg='grey8',font=('Calibri',10))
        name_button = tk.Button(ticker_question_panel, text="Name", command=lambda: self.names_selected(self.root), bg='ivory', fg='grey8',font=('Calibri',10))

        #ticker_name_question.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 5, sticky='ewns')
        ticker_button.grid(row = 0, column = 0, sticky='ewns')
        name_button.grid(row = 0, column = 1, sticky='ewns')
        ticker_question_panel.place(x=230, y=20, anchor='w')

    def add_period_panel(self):
        period_panel = ttk.LabelFrame(self.root, text="Time Period", style = "TLabelframe", labelanchor='n')
        #period_title =  ttk.Label(period_panel, text = "Time Period", style = "TLabel", anchor=tk.CENTER)
        date_format_info = ttk.Label(period_panel, text = "Enter dates in the form yyyy-mm-dd", style="TLabel")
        start_date_question = ttk.Label(period_panel, text = "Start of period:", style="TLabel")
        global start_date_input
        start_date_input = ttk.Entry(period_panel)
        end_date_question = ttk.Label(period_panel, text = "End of period:", style="TLabel")
        global end_date_input
        end_date_input = ttk.Entry(period_panel)

        #period_title.grid(row = 0, column = 0, sticky='ewns', columnspan = 2)
        date_format_info.grid(row = 0, column = 0, sticky='ewns', columnspan = 2)
        start_date_question.grid(row = 1, column = 0, sticky='ewns')
        start_date_input.grid(row = 1, column = 1, sticky='ewns')
        end_date_question.grid(row = 2, column = 0, sticky='ewns')
        end_date_input.grid(row = 2, column = 1, sticky='ewns')
        period_panel.grid(row = 2, column = 0, sticky='ewns')

    def add_retrieve_button(self):
        retrieve_button = tk.Button(self.root, text="Retrieve Data", command=lambda: self.retrieve_data(start_date_input, end_date_input), bg='ivory', fg='grey8',font=('Calibri',10))
        retrieve_button.grid(row = 3, column = 0, sticky='ewns')

    def chosen_service_name(self, service_name):
        print(service_name)
        self.service_name = service_name.lower()
        print(self.service_name)

    def tickers_selected(self, root):
        self.tickers = True

        ticker_panel = ttk.LabelFrame(self.root, text="Company Tickers", style="TLabelframe", labelanchor='n')
        ticker_label = ttk.Label(ticker_panel, text="Enter the list of company tickers separated by a semi-colon (;).")
        ticker_entry = ttk.Entry(ticker_panel)

        ticker_label.grid(row=0, column=0, sticky='ewns')
        ticker_entry.grid(row=1, column=0, sticky='ewns')
        ticker_panel.grid(row=2, column=1)

    def names_selected(self, root):
        self.tickers = False

        name_panel = ttk.LabelFrame(self.root, text="Company Names", style="TLabelframe", labelanchor='n')
        name_label = ttk.Label(name_panel, text="Enter the list of company names separated by a semi-colon (;).")
        name_entry = ttk.Entry(name_panel)

        name_label.grid(row=0, column=0, sticky='ewns')
        name_entry.grid(row=1, column=0, sticky='ewns')
        name_panel.grid(row=2, column=1, sticky='ewns')

    def date_selected(self, date, frame, start = False, end = False):
        if start == True and end == False:
            self.start_date = date
        elif start == False and end == True:
            self.end_date = date
        elif start == True and end == True:
            self.start_date, self.end_date = date

        if self.start_date != False and self.end_date != False:
            frame.destroy()


    def show_date_options_frame(self, unavailable_date, options, start = False, end = False, multiple_dates = False):
        frame = tk.Toplevel(self.root)
        frame.title("Invalid Dates")
        frame.config(bg='black')
        if multiple_dates == False:
            options_label = ttk.Label(frame, text="Unfortunately, no data is available for the date {}.\nThe closest dates are: ".format(unavailable_date))

            option1_button = tk.Button(frame, text=self.option_dates[0], command=lambda: self.date_selected(self.option_dates[0], frame, start, end), bg='ivory', fg='grey8',font=('Calibri',10))
            option2_button = tk.Button(frame, text=self.option_dates[1], command=lambda: self.date_selected(self.option_dates[1], frame, start, end), bg='ivory', fg='grey8',font=('Calibri',10))

            options_ask_to_select_label = ttk.Label(frame, text="Please click one of the available dates.")
            options_label.pack()
            option1_button.pack()
            option2_button.pack()
            options_ask_to_select_label.pack()

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

    def retrieve_data(self, start_date_entry, end_date_entry):
        self.start_date = start_date_entry.get()
        self.end_date = end_date_entry.get()
        data, date_column_name = connect_to_api(self.service_name, "IBM", "NO7SX7BKV0TRLHAM", self.start_date, self.end_date, True)[0:2]
        self.start_date, self.end_date = check_dates(data, date_column_name, self.start_date, self.end_date, True)
        if self.start_date == False and self.end_date != False:
            start_date_str = start_date_entry.get()
            end_date_str = end_date_entry.get()
            self.option_dates = find_nearest_date(data[date_column_name], start_date_str, end_date_str, True)[2]
            self.show_date_options_frame(start_date_str, self.option_dates, start = True)
            #self.root.update_idletasks()
            #self.root.update()

        elif self.end_date == False and self.start_date != False:
            start_date_str = start_date_entry.get()
            end_date_str = end_date_entry.get()
            self.option_dates = find_nearest_date(data[date_column_name], start_date_str, end_date_str, True)[2]
            self.show_date_options_frame(end_date_str, self.option_dates, end = True)

            #self.root.update_idletasks()
            #self.root.update()
        elif self.start_date == False and self.end_date == False:
            start_date_str = start_date_entry.get()
            end_date_str = end_date_entry.get()
            self.option_dates = find_nearest_date(data[date_column_name], start_date_str, end_date_str, True)[2:]
            print(self.option_dates)
            self.show_date_options_frame((start_date_str, end_date_str), self.option_dates, multiple_dates = True)
        # stats_frame, data, date_column_name, new_start, new_end = make_single_frame(self.service_name, "IBM", True, self.start_date, self.end_date)
        # print(stats_frame)
        #return stats_frame

    def clickExitButton(self):
        print("Exiting")
        quit()
