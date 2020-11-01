import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.axes as ax

def time_series(data, date_column_name, reverse_data):
    dates_for_axis = pd.date_range(data[date_column_name][0], data.iloc[-1][date_column_name], freq = 'd')

    #If data is formatted in reverse chronological order, the order is reversed.
    if reverse_data == True:
        data = data.iloc[::-1]

    dates = data[date_column_name]
    open_prices = data["open"]

    fig, ax = plt.subplots(1,1, figsize=(10,6))
    plt.setp(ax, xlabel = "Date (yyyy-mm-dd)", ylabel = "Stock Price ($)")
    ax.plot(dates, open_prices)

    #Set maximum number of axis ticks to 10.
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))

    plt.show()
