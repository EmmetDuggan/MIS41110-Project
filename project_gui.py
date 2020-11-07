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
    service_name = ""
    start_date = "-"
    end_date = ""


    def __init__(self, master=None):
        self.root = tk.Tk()
        self.root.wm_title("Stocks GUI")

        self.s = ttk.Style()
        self.s.configure("TButton", font=("Calibri", 10), foreground = 'grey8', background = 'grey75')
        self.s.configure("TLabel", font=("Calibri",10), foreground = 'grey75', weight="bold", background = 'grey8')
        self.s.configure("TLabelframe", background = 'grey8')


        self.add_api_panel()
        self.add_ticker_panel()
        self.add_period_panel()
        self.add_retrieve_button()

        #self.root.config()
        self.root.geometry("400x300")
        self.root.mainloop()

    def add_api_panel(self):
        api_panel = ttk.LabelFrame(self.root, style = "TLabelframe")
        api_name_question = ttk.Label(api_panel, text = "Service Name", style="TLabel", anchor=tk.CENTER)
        alphavantage_button = tk.Button(api_panel, text="AlphaVantage", command = lambda: self.chosen_service_name("AlphaVantage"), bg='ivory', fg='grey8',font=('Calibri',10))
        macrotrends_button = tk.Button(api_panel, text="MacroTrends", command = lambda: self.chosen_service_name("MacroTrends"), bg='ivory', fg='grey8',font=('Calibri',10))

        api_name_question.grid(row = 0,  column = 0, columnspan = 2,padx = 10, pady = 5, sticky='ewns')
        alphavantage_button.grid(row = 1, column = 0, sticky='ewns')
        macrotrends_button.grid(row = 1, column = 1, sticky='ewns')
        api_panel.grid(row = 0, column = 0, sticky='ewns')

    def add_ticker_panel(self):
        ticker_question_panel = ttk.LabelFrame(self.root, style = "TLabelframe")
        ticker_name_question = ttk.Label(ticker_question_panel, text = "Search By", style="TLabel", anchor=tk.CENTER)
        ticker_button = tk.Button(ticker_question_panel, text="Ticker", command=self.tickers_selected, bg='ivory', fg='grey8',font=('Calibri',10))
        name_button = tk.Button(ticker_question_panel, text="Name", command=self.names_selected, bg='ivory', fg='grey8',font=('Calibri',10))

        ticker_name_question.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 5, sticky='ewns')
        ticker_button.grid(row = 1, column = 0, sticky='ewns')
        name_button.grid(row = 1, column = 1, sticky='ewns')
        ticker_question_panel.grid(row = 0, column = 1, sticky='ewns')

    def add_period_panel(self):
        period_panel = ttk.LabelFrame(self.root, style = "TLabelframe")
        period_title =  ttk.Label(period_panel, text = "Time Period", style = "TLabel", anchor=tk.CENTER)
        date_format_info = ttk.Label(period_panel, text = "Enter dates in the form yyyy-mm-dd", style="TLabel")
        start_date_question = ttk.Label(period_panel, text = "Start of period:", style="TLabel")
        global start_date_input
        start_date_input = ttk.Entry(period_panel)
        end_date_question = ttk.Label(period_panel, text = "End of period:", style="TLabel")
        global end_date_input
        end_date_input = ttk.Entry(period_panel)

        period_title.grid(row = 0, column = 0, sticky='ewns', columnspan = 2)
        date_format_info.grid(row = 1, column = 0, sticky='ewns', columnspan = 2)
        start_date_question.grid(row = 2, column = 0, sticky='ewns')
        start_date_input.grid(row = 2, column = 1, sticky='ewns')
        end_date_question.grid(row = 3, column = 0, sticky='ewns')
        end_date_input.grid(row = 3, column = 1, sticky='ewns')
        period_panel.grid(row = 2, column = 0, sticky='ewns')

    def add_retrieve_button(self):
        retrieve_button = tk.Button(self.root, text="Retrieve Data", command=lambda: self.retrieve_data(start_date_input, end_date_input), bg='ivory', fg='grey8',font=('Calibri',10))
        retrieve_button.grid(row = 3, column = 0, sticky='ewns')

    def chosen_service_name(self, service_name):
        print(service_name)
        self.service_name = service_name.lower()
        print(self.service_name)

    def tickers_selected(self):
        self.tickers = True
        print(self.tickers)

    def names_selected(self):
        self.tickers = False
        print(self.tickers)

    def show_date_options_frame(self, unavailable_date, options):
        frame = tk.Toplevel()
        frame.title("Invalid Dates")
        options_label = ttk.Label(frame, text="Unfortunately, no data is available for the date " + unavailable_date + ".\nThe closest dates are: " + options)
        options_label.pack()
        frame.mainloop()
        self.root.update()

    def retrieve_data(self, start_date_entry, end_date_entry):
        self.start_date = start_date_entry.get()
        self.end_date = end_date_entry.get()
        data, date_column_name = connect_to_api(self.service_name, "IBM", "NO7SX7BKV0TRLHAM", self.start_date, self.end_date, True)[0:2]
        self.start_date, self.end_date = check_dates(data, date_column_name, self.start_date, self.end_date, True)
        if self.start_date == False:
            options = find_nearest_date(data[date_column_name], self.start_date, self.end_date, True)
            self.show_date_options_frame(start_date_entry.get(), options)
            self.root.update_idletasks()
            self.root.update()
            print("Incorrect")
        elif self.end_date == False:
            self.show_date_options_frame
        elif self.start_date == False and self.end_date == False:
            self.show_date_options_frame
        # stats_frame, data, date_column_name, new_start, new_end = make_single_frame(self.service_name, "IBM", True, self.start_date, self.end_date)
        # print(stats_frame)
        #return stats_frame

    def clickExitButton(self):
        print("Exiting")
        quit()




#root = Tk()
#app = MenuWindow()
#app.add_api_panel()
#app.add_period_panel()
#root.wm_title("Stocks GUI")

#root.geometry("400x300")
#root.mainloop()
