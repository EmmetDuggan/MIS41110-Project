import numpy as np
import pandas as pd
#from scipy.optimize import curve_fit

def dictionary_values_to_series(stats):
    vals = np.array([val for val in stats.values()])
    stat_names = stats.keys()
    return pd.Series(data = vals, index = stat_names)

def compute_descriptive_stats(price_data):
    mean = np.mean(price_data)
    std = np.std(price_data)
    max_price = max(price_data)
    min_price = min(price_data)
    range = max_price - min_price
    quartile_25 = np.quantile(price_data, 0.25)
    quartile_75 = np.quantile(price_data, 0.75)
    interquartile_range = quartile_75 - quartile_25

    return {"Mean": mean, "Standard Deviation": std, "Maximum Price": max_price,
     "Minimum Price": min_price, "Range": range, "25th Quartile": quartile_25,
     "75th Quartile": quartile_75, "Interquartile Range": interquartile_range}

#Creating a DataFrame with the types of statistics as the indices and company
#ticker as the column.
def make_stats_frame(stats, ticker):
    df = pd.DataFrame(dictionary_values_to_series(stats), columns = [ticker])
    return df

#Function to add different company statistics to the DataFrame
def add_to_frame(stats, ticker, frame):
    frame[ticker] = dictionary_values_to_series(stats)
    return frame


#https://towardsdatascience.com/the-complete-guide-to-time-series-analysis-and-forecasting-70d476bfe775
# def ts_moving_average_exponential(price_data, period):
#     rolling_mean = price_data.rolling(window = period).mean()
#     return rolling_mean



# def plot_moving_average(series, window, plot_intervals=False, scale=1.96):
#
#     rolling_mean = series.rolling(window=window).mean()
#
#     plt.figure(figsize=(17,8))
#     plt.title('Moving average\n window size = {}'.format(window))
#     plt.plot(rolling_mean, 'g', label='Rolling mean trend')
#
#     #Plot confidence intervals for smoothed values
#     if plot_intervals:
#         mae = mean_absolute_error(series[window:], rolling_mean[window:])
#         deviation = np.std(series[window:] - rolling_mean[window:])
#         lower_bound = rolling_mean - (mae + scale * deviation)
#         upper_bound = rolling_mean + (mae + scale * deviation)
#         plt.plot(upper_bound, 'r--', label='Upper bound / Lower bound')
#         plt.plot(lower_bound, 'r--')
#
#     plt.plot(series[window:], label='Actual values')
#     plt.legend(loc='best')
#     plt.grid(True)
#
# #Smooth by the previous 5 days (by week)
# plot_moving_average(data.CLOSE, 5)
#
# #Smooth by the previous month (30 days)
# plot_moving_average(data.CLOSE, 30)
#
# #Smooth by previous quarter (90 days)
# plot_moving_average(data.CLOSE, 90, plot_intervals=True)
