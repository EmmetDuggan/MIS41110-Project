import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import matplotlib.axes as ax

plt.rc('font', family = 'serif')
plt.rcParams['figure.figsize'] = (14,5)
plt.rcParams['font.size'] = 8.
plt.rcParams['axes.titlesize'] = 'small'
plt.rcParams['axes.labelsize'] = 'small'
plt.rcParams['xtick.labelsize'] = 'small'
plt.rcParams['ytick.labelsize'] = 'small'

def plot_arrangement(data_sets):
    no_cols = len(data_sets)/2

    uneven = False
    if no_cols % 2 != 0:
        no_cols += 0.5
        uneven = True
    return 2, int(no_cols), uneven

def set_layout(axis):
    axis.xaxis.set_major_locator(plt.MaxNLocator(10))
    axis.yaxis.set_major_locator(plt.MaxNLocator(10))
    axis.set_xlabel("Date (yyyy-mm-dd)")
    axis.set_ylabel("Stock Price ($)")
    xlabels = axis.get_xticklabels()
    axis.set_xticklabels(xlabels, rotation = 45)

def make_time_series(axis, data, dates, ticker):
    open_prices = data["open"]
    axis.plot(dates, open_prices)
    axis.set_title(ticker)
    set_layout(axis)

def plot_single_time_series(data, ticker, date_column_name, reverse_data = False):
    #If data is formatted in reverse chronological order, the order is reversed.
    if reverse_data == True:
        data = data.iloc[::-1]

    dates = data[date_column_name]
    open_prices = data["open"]

    fig, ax = plt.subplots(1, 1, figsize=(10,6))
    set_layout(ax)
    ax.plot(dates, open_prices)
    plt.show()

def plot_multiple_time_series(data_sets, tickers, date_column_name, reverse_data = False):
    #If data is formatted in reverse chronological order, the order is reversed.
    if reverse_data == True:
        for data in data_sets:
            data = data.iloc[::-1]

    dates = data_sets[0][date_column_name]

    no_rows, no_cols, uneven = plot_arrangement(data_sets)
    fig, axs = plt.subplots(no_rows, no_cols, figsize=(10,6))
    #ax.setp(ax, xlabel = "Date (yyyy-mm-dd)", ylabel = "Stock Price ($)")

    data_index = 0
    print(no_rows, no_cols)
    for i in range(no_rows):
        for j in range(no_cols):
            if uneven == True:
                if data_index < len(data_sets):
                    make_time_series(axs[i,j], data_sets[data_index], dates, tickers[data_index])
                    data_index += 1
                else:
                    fig.delaxes(axs[i,j])
            else:
                make_time_series(axs[i,j], data_sets[data_index], dates, tickers[data_index])
                data_index += 1



    plt.show()


# with sb.axes_style('white'):
#     fig, axs = subplots(2,4, figsize=(14,5), sharex=True)
#     ls, lc = ['-','--','--'], ['k', '0.5', '0.5']
#     percs = [percentile(lpf.sampler.chain[:,:,i], [50,16,84], 0) for i in range(8)]
#     [axs.flat[i].plot(lpf.sampler.chain[:,:,i].T, 'k', alpha=0.0025) for i in range(8)]
#     [[axs.flat[i].plot(percs[i][j], c=lc[j], ls=ls[j]) for j in range(3)] for i in range(8)]
#     setp(axs, yticks=[], xlim=[0,mc_iter//thin])
#     fig.tight_layout()
