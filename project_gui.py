from project_io import connect_to_api, search_for_tickers
from project_calendar import get_valid_dates, find_nearest_date
from project_data_visualisation import plot_single_time_series, plot_multiple_time_series
from project_descriptive_stats import compute_descriptive_stats, make_stats_frame, add_to_frame
import numpy as np
from tkinter import *

class MenuWindow():

    def __init__(self, master=None):
        self.root = Tk()

        self.period_panel = LabelFrame(self.root, bg='cyan')
        self.start_date_question = Label(self.period_panel, text = "Start of period:")
        self.start_date_input = Entry(self.period_panel)
        self.end_date_question = Label(self.period_panel, text = "End of period:")
        self.end_date_input = Entry(self.period_panel)
        self.start_date_question.pack()
        self.start_date_input.pack()
        self.end_date_question.pack()
        self.end_date_input.pack()
        self.period_panel.pack()

        self.api_panel = LabelFrame(self.root, bg='red')
        self.api_name_question = Label(self.api_panel, text = "Service name:").pack()
        self.alphavantage_button = Button(self.api_panel, text="AlphaVantage", command=self.clickExitButton).pack()
        self.macrotrends_button = Button(self.api_panel, text="MacroTrends", command=self.clickExitButton).pack()
        self.api_panel.pack()

        self.ticker_name_question = Label(self, text = "Search by:").pack(side=LEFT)
        self.ticker_button = Button(self, text="Ticker", command=self.clickExitButton).pack()
        self.name_button = Button(self, text="Name", command=self.clickExitButton).pack()

        #
        # self.buttonForget.pack()
        # self.buttonRecover.pack()
        # self.label.pack(side="bottom")
        self.root.mainloop()

    def clickExitButton(self):
        print("Pressed the button!")
        exit()

    def add_api_panel(self):
        api_name_question = Label(self, text = "Service name:").pack()
        alphavantage_button = Button(self, text="AlphaVantage", command=self.clickExitButton).pack()
        macrotrends_button = Button(self, text="MacroTrends", command=self.clickExitButton).pack()

    def add_ticker_panel(self):
        ticker_name_question = Label(self, text = "Search by:").pack(side=LEFT)
        ticker_button = Button(self, text="Ticker", command=self.clickExitButton).pack()
        name_button = Button(self, text="Name", command=self.clickExitButton).pack()

    def add_period_panel(self):


        start_date_question = Label(self.period_panel, text = "Start of period:")
        start_date_input = Entry(self.period_panel)
        end_date_question = Label(self.period_panel, text = "End of period:")
        end_date_input = Entry(self.period_panel)
        self.period_panel.pack()

#root = Tk()
app = MenuWindow()
#app.add_api_panel()
#app.add_ticker_panel()
#app.add_period_panel()
#root.wm_title("Stocks GUI")

#root.geometry("400x300")
#root.mainloop()
