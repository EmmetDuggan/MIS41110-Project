import numpy as np
import pandas as pd

def dictionary_values_to_series(stats):
    """Converts values from dictionary returned by compute_descriptive_stats function into a pandas Series object."""
    vals = np.array([val for val in stats.values()])
    stat_names = stats.keys()
    return pd.Series(data = vals, index = stat_names)

def compute_descriptive_stats(price_data):
    """Calculates basic descriptive statistics for input share prices."""
    mean = np.mean(price_data)
    std = np.std(price_data)
    max_price = max(price_data)
    min_price = min(price_data)
    range = max_price - min_price
    quartile_25 = np.quantile(price_data, 0.25)
    quartile_75 = np.quantile(price_data, 0.75)
    interquartile_range = quartile_75 - quartile_25

    return {"Mean": np.round(mean,2), "Standard Deviation": np.round(std,2), "Maximum Price": np.round(max_price,2),
     "Minimum Price": np.round(min_price,2), "Range": np.round(range,2), "25th Quartile": np.round(quartile_25,2),
     "75th Quartile": np.round(quartile_75,2), "Interquartile Range": np.round(interquartile_range,2)}


def make_stats_frame(stats, ticker):
    """Creates a DataFrame with the types of statistics as the indices and company ticker as the column."""
    df = pd.DataFrame(dictionary_values_to_series(stats), columns = [ticker])
    return df

def add_to_frame(stats, ticker, frame):
    """Add different company statistics to the DataFrame when multiple companies are queried."""
    frame[ticker] = dictionary_values_to_series(stats)
    return frame
