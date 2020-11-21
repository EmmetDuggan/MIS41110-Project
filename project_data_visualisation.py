import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import matplotlib.axes as ax
import datetime
from project_io import search_for_names
from project_predictive_stats import time_series_seasonal, create_arima_forecast, time_series_training, time_series_forecast, linear_regression


#from project_descriptive_stats import ts_moving_average_exponential
plt.style.use("dark_background")
plt.rc('font', family = 'serif')
plt.rcParams['figure.figsize'] = (14,5)
plt.rcParams['font.size'] = 8.
plt.rcParams['axes.titlesize'] = 'small'
plt.rcParams['axes.labelsize'] = 'small'
plt.rcParams['axes.titlepad'] = 4
plt.rcParams['xtick.labelsize'] = 'small'
plt.rcParams['ytick.labelsize'] = 'small'
plt.rcParams['grid.linewidth'] = 0.15

class DataSets():

    def __init__(self):
        self.tickers = []
        self.sets = []
        self.dates = []

    def add_data(self, data):
        self.sets.append(data)
    def add_dates(self, dates):
        try:
            self.dates.append(dates.values)
        except AttributeError:
            self.dates.append(dates)
    def add_ticker(self, ticker):
        self.tickers.append(ticker)

    def join_data_to_ticker(self):
        for i in range(len(self.sets)):
            self.sets[i]["ticker"] = [self.tickers[i]]*len(self.sets[i])
            if "date" not in self.sets[i].columns:
                self.sets[i]["date"] = self.dates[i]

    def combine_all_data(self):
        df = self.sets[0]
        for i in range(1, len(self.sets)):
            print(i)
            df = df.append(self.sets[i], ignore_index = True)
        return df

def make_ds(data_sets, tickers, date_column_name, reverse_data = False):
    ds = DataSets()
    for data, ticker in zip(data_sets, tickers):
        if date_column_name != "yahoo":
            ds.add_data(data)
            ds.add_dates(data[date_column_name])
            ds.add_ticker(ticker)
        else:
            ds.add_data(data)
            ds.add_dates([datetime.datetime.strftime(date, '%Y-%m-%d') for date in data.index])
            ds.add_ticker(ticker)
    ds.join_data_to_ticker()
    return ds


def plot_arrangement(data_sets):
    no_cols = len(data_sets)
    even = True
    if no_cols % 2 != 0:
        no_cols += 0.5
        even = False
    return 2, int(no_cols), even

def set_layout(axis, dates):
    axis.set_xlabel("Date (yyyy-mm-dd)")
    axis.set_ylabel("Stock Price ($)")
    xlabels = axis.get_xticklabels()
    axis.set_xticklabels(dates, rotation = 45)

def make_time_series(axis, data, dates, ticker, company_name = ""):
    open_prices = data["open"]
    axis.plot(dates, open_prices)
    axis.set_title("{} ({})".format(company_name.title(), ticker))
    #set_layout(axis, dates)

def plot_raw_time_series(data, ticker, date_column_name, reverse_data = False):
    #Accounting for different format of Yahoo! data.
    if date_column_name != "yahoo":
        dates = data[date_column_name]
    else:
        dates = [datetime.datetime.strftime(date, '%Y-%m-%d') for date in data.index]

    company_name = search_for_names(ticker)[0]
    open_prices = data["open"]
    fig, ax = sb.subplots(1, 1, figsize=(10,6))
    set_layout(ax, dates)
    ax.set_title("{} ({})".format(company_name.title(), ticker))
    ax.plot(dates, open_prices)
    plt.show()

def plot_time_series_forecasts(data_sets, tickers, date_column_name, period = "d", steps = 24, reverse_data = False):

    ds = make_ds(data_sets, tickers, date_column_name)

    no_rows, no_cols, even = plot_arrangement(ds.sets)
    company_names = search_for_names(tickers)

    fig = plt.figure()

    for i in range(len(ds.sets)):
        y, times, future_times, fitted_values, ci_upper, ci_lower, predicted_values, predicted_ci_upper, predicted_ci_lower = linear_regression(ds.sets[i], period, steps)
        results = create_arima_forecast(ds.sets[i], period)
        arima_predicted_uc, arima_predicted_ci = time_series_forecast(results, steps)

        if i <= len(ds.sets):
            ax = fig.add_subplot(2, no_cols, i+1)
            arima_ax = fig.add_subplot(2, no_cols, len(ds.sets)+i+1)

            ax.plot(times, y["close"], label="Data")
            ax.plot(times, fitted_values, '-', color = '#bfbbd9', label="Linear Fit")
            ax.plot(times, ci_upper, '-', linewidth = 0.1, color = '#bfbbd9')
            ax.plot(times, ci_lower, '-', linewidth = 0.1, color = '#bfbbd9',)
            ax.plot(future_times, predicted_values, '--', color = '#feffb3', label="Linear\nPrediction")
            ax.plot(future_times, predicted_ci_upper, '--', linewidth = 0.1, color = '#feffb3',)
            ax.plot(future_times, predicted_ci_lower, '--', linewidth = 0.1, color = '#feffb3',)
            ax.fill_between(times, ci_upper, ci_lower, color = '#81b1d2', alpha = 0.5)
            ax.fill_between(future_times, predicted_ci_upper, predicted_ci_lower, color = '#81b1d2', alpha = 0.5)
            #ax.set_xticklabels(ax.get_xticklabels(), rotation = 45)
            ax.grid()

            if len(company_names) == len(tickers):
                ax.set_title("{} ({})\nLinear Regression Model".format(company_names[i].title(), ds.tickers[i]))
            else:
                ax.set_title("{}\nLinear Regression Model".format(ds.tickers[i]))



            if i == 0:
                ax.set_ylabel("Stock Price ($)")
                arima_ax.set_ylabel("Stock Price ($)")
            else:
                ax.set_ylabel("")
                arima_ax.set_ylabel("")

            arima_ax.plot(y.index, y["close"], label='Observed')
            arima_predicted_uc.predicted_mean.plot(ax=arima_ax, label='ARIMA\nPrediction')
            arima_ax.fill_between(arima_predicted_ci.index, arima_predicted_ci.iloc[:, 0], arima_predicted_ci.iloc[:, 1], color='#81b1d2', alpha=.25)
            arima_ax.set_xlabel('Date (yyyy-mm-dd)')
            #arima_ax.set_xticklabels(arima_ax.get_xticklabels(), rotation = 45)
            arima_ax.grid()
            arima_ax.set_title("ARIMA Model")

            if i == len(ds.sets)-1:
                ax.legend(bbox_to_anchor = (1.20,0.5))
                arima_ax.legend(bbox_to_anchor = (1.20,0.5))

    fig.tight_layout(pad=3.)
    #plt.show()
    return fig


def plot_linear_regression(data_sets, tickers, date_column_name, period = "d", steps = 24, reverse_data = False):

    ds = make_ds(data_sets, tickers, date_column_name)
    y, times, future_times, fitted_values, ci_upper, ci_lower, predicted_values, predicted_ci_upper, predicted_ci_lower = linear_regression(ds.sets[0], period, steps)

    fig = plt.figure()
    plt.plot(times, y["close"], label="Data")
    plt.plot(times, fitted_values, '-', color = '#bfbbd9', label="Linear Fit")
    plt.plot(times, ci_upper, '-', linewidth = 0.1, color = '#bfbbd9')
    plt.plot(times, ci_lower, '-', linewidth = 0.1, color = '#bfbbd9',)
    plt.plot(future_times, predicted_values, '--', color = '#feffb3', label="Linear Prediction")
    plt.plot(future_times, predicted_ci_upper, '--', linewidth = 0.1, color = '#feffb3',)
    plt.plot(future_times, predicted_ci_lower, '--', linewidth = 0.1, color = '#feffb3',)
    plt.fill_between(times, ci_upper, ci_lower, color = '#81b1d2', alpha = 0.5)
    plt.fill_between(future_times, predicted_ci_upper, predicted_ci_lower, color = '#81b1d2', alpha = 0.5)
    plt.xlabel("Stock Price ($)")
    plt.ylabel("Date")
    plt.legend()

    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    print(colors)

    # if company_name is None:
    #     plt.title("name ({})".format(ticker))
    # else:
    plt.title("{}".format(ds.tickers[0]))

    #plt.show()
    return fig



    data_index = 0
    print(no_rows, no_cols)
    for i in range(no_rows):
        for j in range(no_cols):
            if uneven == True:
                if data_index < len(data_sets):
                    if len(company_names) == len(tickers):
                        make_time_series(axs[i,j], data_sets[data_index], dates, tickers[data_index], company_names[data_index])
                    else:
                        make_time_series(axs[i,j], data_sets[data_index], dates, tickers[data_index])
                    data_index += 1
                else:
                    fig.delaxes(axs[i,j])
            else:
                if len(company_names) == len(tickers):
                    make_time_series(axs[i,j], data_sets[data_index], dates, tickers[data_index], company_names[data_index])
                else:
                    make_time_series(axs[i,j], data_sets[data_index], dates, tickers[data_index])
                data_index += 1

    # grid = plt.GridSpec(4, 4, hspace=0.2, wspace=0.2)
    # main_ax = fig.add_subplot(grid[:-1, 1:])
    # y_hist = fig.add_subplot(grid[:-1, 0], xticklabels=[], sharey=main_ax)
    # x_hist = fig.add_subplot(grid[-1, 1:], yticklabels=[], sharex=main_ax)
    # # scatter points on the main axes
    # main_ax.plot(x, y, 'ok', markersize=3, alpha=0.2)
    #
    # # histogram on the attached axes
    # x_hist.hist(x, 40, histtype='stepfilled',
    #             orientation='vertical', color='gray')
    # x_hist.invert_yaxis()
    #
    # y_hist.hist(y, 40, histtype='stepfilled',
    #             orientation='horizontal', color='gray')
    # y_hist.invert_xaxis()



#########################################################

#https://www.learndatasci.com/tutorials/predicting-housing-prices-linear-regression-using-python-pandas-statsmodels/

#https://towardsdatascience.com/an-end-to-end-project-on-time-series-analysis-and-forecasting-with-python-4835e6bf050b

#https://towardsdatascience.com/moving-averages-in-python-16170e20f6c


#########################################################


    # no_rows, no_cols, even = plot_arrangement(data_sets)
    # print(even)
    # fig, axs = sb.subplots(no_rows, no_cols, figsize=(10,6))
    # sb.locator_params(axis='x', nbins=8)
    #
    # company_names = search_for_names(tickers)
    #
    # data_index = 0
    # for i in range(no_rows):
    #     for j in range(no_cols):
    #         if even == True:
    #             # if data_index < len(data_sets):
    #             if len(company_names) == len(tickers):
    #                 print(i,j,data_index)
    #                 make_time_series(axs[i,j], data_sets[data_index], dates_sets[data_index], tickers[data_index], company_names[data_index])
    #             else:
    #                 print(i,j,data_index)
    #                 make_time_series(axs[i,j], data_sets[data_index], dates_sets[data_index], tickers[data_index])
    #             data_index += 1
    #             # else:
    #             #     fig.delaxes(axs[i,j])
    #         else:
    #             if data_index < len(data_sets):
    #                 if len(company_names) == len(tickers):
    #                     print("Making time series i,j:",i,j)
    #                     make_time_series(axs[i,j], data_sets[data_index], dates_sets[data_index], tickers[data_index], company_names[data_index])
    #                 else:
    #                     print("Making time series i,j:",i,j)
    #                     make_time_series(axs[i,j], data_sets[data_index], dates_sets[data_index], tickers[data_index])
    #                 data_index += 1
    #             else:
    #                 fig.delaxes(axs[i,j])
    #
    # plt.show()


# with sb.axes_style('white'):
#     fig, axs = subplots(2,4, figsize=(14,5), sharex=True)
#     ls, lc = ['-','--','--'], ['k', '0.5', '0.5']
#     percs = [percentile(lpf.sampler.chain[:,:,i], [50,16,84], 0) for i in range(8)]
#     [axs.flat[i].plot(lpf.sampler.chain[:,:,i].T, 'k', alpha=0.0025) for i in range(8)]
#     [[axs.flat[i].plot(percs[i][j], c=lc[j], ls=ls[j]) for j in range(3)] for i in range(8)]
#     setp(axs, yticks=[], xlim=[0,mc_iter//thin])
#     fig.tight_layout()
