import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from project_io import search_for_names
from project_predictive_stats import time_series_seasonal, create_arima_forecast, time_series_training, time_series_forecast, linear_regression

# https://plotly.com/python/time-series/
# https://medium.com/@srkhedkar/stock-market-prediction-using-python-article-1-the-straight-line-c23f26579b4d


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

def plot_arrangement(data_sets):
    """Sets the columns and rows of the subplot arrangement."""
    no_cols = len(data_sets)
    even = True
    if no_cols % 2 != 0:
        no_cols += 0.5
        even = False
    return 2, int(no_cols), even

def set_layout(axis, dates, title):
    axis.set_title(title)
    axis.grid()

def make_time_series(axis, data, dates, ticker, company_name = ""):

    close_prices = data["close"]
    set_layout(axis, dates, "{} ({})".format(company_name.title(), ticker))
    axis.plot(dates, close_prices)

def plot_raw_time_series(data, ticker, reverse_data = False):
    """Plots basic raw time series of a single company."""
    dates = [datetime.datetime.strftime(date, '%Y-%m-%d') for date in data.index]

    company_name = search_for_names(ticker)[0]
    close_prices = data["close"]
    fig = plt.figure()
    fig.plot(dates, close_prices)
    plt.show()

def plot_time_series_forecasts(data_sets, tickers, future_date, period = "d", steps = 24, reverse_data = False):
    """Plots time series forecasts for both the linear and ARIMA models. Returns the plot
    along with the linear model RMSE, R^2 values for each company and the predicted maximum/
    minimum prices from each model."""
    no_rows, no_cols, even = plot_arrangement(data_sets)
    company_names = search_for_names(tickers)

    fig = plt.figure()
    rmse_list = []
    r2_list = []
    arima_max = []
    arima_min = []
    linear_max = []
    linear_min = []

    for i in range(len(data_sets)):
        #Perform linear regression, ARIMA modeling on each data set from the separate companies.
        y, times, future_times, fitted_values, ci_upper, ci_lower, predicted_values, predicted_ci_upper, predicted_ci_lower, r, rmse = linear_regression(data_sets[i], period, steps, future_date)
        results = create_arima_forecast(data_sets[i], period)
        arima_comparison, arima_comparison_ci = time_series_training(results, y)
        arima_predicted_uc, arima_predicted_ci = time_series_forecast(results, steps, future_date)
        arima_max.append(arima_comparison_ci.iloc[-1, 1])
        arima_min.append(arima_comparison_ci.iloc[-1, 0])
        linear_max.append(predicted_ci_upper[-1])
        linear_min.append(predicted_ci_lower[-1])
        rmse_list.append(np.round(rmse,3))
        r2_list.append(np.round(r**2,3))

        if i <= len(data_sets):
            #Linear model will be shown on the first row, with the ARIMA forecast underneath.
            ax = fig.add_subplot(2, no_cols, i+1)
            arima_ax = fig.add_subplot(2, no_cols, len(data_sets)+i+1)

            #Setting the plot parameters for the linear regression plot and plotting data.
            ax.plot(times, y["close"], label="Data")
            ax.plot(times, fitted_values, '-', color = '#bfbbd9', label="Linear Fit")
            ax.plot(times, ci_upper, '-', linewidth = 0.1, color = '#bfbbd9')
            ax.plot(times, ci_lower, '-', linewidth = 0.1, color = '#bfbbd9',)
            ax.plot(future_times, predicted_values, '--', color = '#feffb3', label="Linear\nPrediction")
            ax.plot(future_times, predicted_ci_upper, '--', linewidth = 0.1, color = '#feffb3',)
            ax.plot(future_times, predicted_ci_lower, '--', linewidth = 0.1, color = '#feffb3',)

            #Filling between the predicted share maximum/minimum for the linear model.
            ax.fill_between(times, ci_upper, ci_lower, color = '#81b1d2', alpha = 0.5)
            ax.fill_between(future_times, predicted_ci_upper, predicted_ci_lower, color = '#81b1d2', alpha = 0.5)
            ax.set_ylim(min(y["close"])-0.2*np.mean(y["close"]),max(y["close"])+0.2*np.mean(y["close"]))

            #If the company names were found, add the name to the title.
            if len(company_names) == len(tickers):
                set_layout(ax, times, "{} ({})\nLinear Regression Model: $R^2 = $ {}; RMSE = {}".format(company_names[i].title(), tickers[i], np.round(r**2,3), np.round(rmse,3)))
            else:
                set_layout(ax, times, "{}\nLinear Regression Model: $R^2 = $ {}; RMSE = {}".format(tickers[i], np.round(r**2,3), np.round(rmse,3)))

            if i == 0:
                ax.set_ylabel("Stock Price ($)")
                arima_ax.set_ylabel("Stock Price ($)")
            else:
                ax.set_ylabel("")
                arima_ax.set_ylabel("")

            #Setting the ARIMA forecast plot parameters.
            arima_ax.plot(y.index, y["close"], label='Observed')
            arima_predicted_uc.predicted_mean.plot(ax=arima_ax, label='ARIMA\nPrediction')
            arima_comparison.predicted_mean.plot(ax=arima_ax, label='ARIMA\nTraining', alpha=.7)

            #Filling between the predicted share maximum/minimum for the ARIMA model.
            arima_ax.fill_between(arima_predicted_ci.index, arima_predicted_ci.iloc[:, 0], arima_predicted_ci.iloc[:, 1], color='#81b1d2', alpha=.25)
            arima_ax.fill_between(arima_comparison_ci.index,arima_comparison_ci.iloc[:, 0],arima_comparison_ci.iloc[:, 1], color='k', alpha=.2)
            arima_ax.set_ylim(min(y["close"])-0.1*np.mean(y["close"]),max(y["close"])+0.1*np.mean(y["close"]))
            set_layout(arima_ax, times, "ARIMA Model")

            #Placing legends outside plot for clarity.
            if i == len(data_sets)-1:
                ax.legend(bbox_to_anchor = (1.20,0.5))
                arima_ax.legend(bbox_to_anchor = (1.20,0.5))


    fig.tight_layout(pad=3.)
    fig.canvas.set_window_title('Linear Regression & ARIMA Forecasting (All Companies)')
    return fig, rmse_list, r2_list, np.round(linear_min,2), np.round(linear_max,2), np.round(arima_min,2), np.round(arima_max,2)


def plot_linear_regression(data_sets, tickers, future_date, period = "d", steps = 24, reverse_data = False):
    """Plots the linear regression model for a single company."""
    #Perform linear regression on data from a single company.
    y, times, future_times, fitted_values, ci_upper, ci_lower, predicted_values, predicted_ci_upper, predicted_ci_lower, r, rmse = linear_regression(data_sets[0], period, steps, future_date)
    linear_min, linear_max = predicted_ci_upper[-1], predicted_ci_lower[-1]

    fig = plt.figure()
    #Setting the plot parameters for the linear regression plot and plotting data.
    plt.plot(times, y["close"], label="Data")
    plt.plot(times, fitted_values, '-', color = '#bfbbd9', label="Linear Fit")
    plt.plot(times, ci_upper, '-', linewidth = 0.1, color = '#bfbbd9')
    plt.plot(times, ci_lower, '-', linewidth = 0.1, color = '#bfbbd9',)
    plt.plot(future_times, predicted_values, '--', color = '#feffb3', label="Linear Prediction")
    plt.plot(future_times, predicted_ci_upper, '--', linewidth = 0.1, color = '#feffb3',)
    plt.plot(future_times, predicted_ci_lower, '--', linewidth = 0.1, color = '#feffb3',)
    plt.fill_between(times, ci_upper, ci_lower, color = '#81b1d2', alpha = 0.5)
    plt.fill_between(future_times, predicted_ci_upper, predicted_ci_lower, color = '#81b1d2', alpha = 0.5)
    plt.xlabel("Date (yyyy-mm-dd)")
    plt.ylabel("Stock Price ($)")
    plt.grid()
    plt.legend()

    plt.title("{}".format(tickers[0]))
    fig.canvas.set_window_title('Linear Regression (First Company: {})'.format(tickers[0]))
    return fig, rmse, r**2, np.round(linear_min,2), np.round(linear_max,2)
