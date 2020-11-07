from project_io import connect_to_api, search_for_tickers
from project_calendar import get_valid_dates, find_nearest_date
from tkinter import Tk, font

from project_gui import MenuWindow

win = MenuWindow()
print(win.service_name)

# start_date = input("Enter start date:")
# end_date = input("Enter end date:")
# data, date_column_name, reverse_data = connect_to_api("alphavantage", "V", "NO7SX7BKV0TRLHAM", start_date, end_date)

#print(data[date_column_name])
#find_nearest_date(data[date_column_name], start_date, end_date)

# print(search_for_tickers(["Zumiez Inc.", "Zynga Inc."]))
#
# def p_text():
#     print("Alright")
#
# win = tk.Tk()
# win.title("Stocks GUI")
# label_ticker_or_name = tk.Label(win, text = "Would you like to search by \nticker symbol or company name?").pack()
# button_ticker = tk.Button(win, text = "Ticker", command = p_text()).pack(side = tk.LEFT)
# button_name = tk.Button(win, text = "Name").pack(side = tk.LEFT)
# win.mainloop()
