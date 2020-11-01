import numpy as np
import pandas as pd

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
