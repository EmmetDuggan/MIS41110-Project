import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress
import itertools
import warnings

warnings.filterwarnings("ignore")

def format_data(data, period):
    """Formats the input data into a form which can be used by the ARIMA forecasting model."""
    cols = data.columns
    #Dropping unused columns.
    data = data.drop([col for col in cols if col != "date" and col != "close"], axis = 1)
    #Convert frame index to datetime objects.
    data.index = pd.to_datetime(data.index)
    return data.resample(period).mean()

def linear_fit(x, m, c):
    """Defines the linear model."""
    return x*m + c

def gradient_matrix(x):
    """Matrix representation of line of best fit partial derivatives. Used to compute the confidence intervals."""
    return np.array([[x],[1]])

def compute_rmse(actual_values, fitted_values):
    """Computes the root-mean-square error between the fitted values and observed share prices."""
    return np.sqrt(sum(((actual_values - fitted_values)**2)/len(actual_values)))

def compute_linear_confidence_interval(x, y):
    """Computes the confidence interval for the linear model best-fit line over the training period."""
    #Get slope, y-intercept, covariance matrix from best-fit line.
    pars, cov = curve_fit(linear_fit, x, y)
    fit_vals = np.array([linear_fit(z, *pars) for z in x])
    #Return matrix product of covariance matrix with gradient matrix to get confidence interval values.
    return fit_vals, np.sqrt(np.array([float(gradient_matrix(z).T @ cov @ gradient_matrix(z)) for z in x])), pars, cov

def predict_linear_confidence_interval(x, pars, cov):
    """Computes the confidence interval over which the linear model predicts the share price will be between."""
    fit_vals = np.array([linear_fit(z, *pars) for z in x])
    return fit_vals, np.sqrt(np.array([float(gradient_matrix(z).T @ cov @ gradient_matrix(z)) for z in x]))


def generate_future_times(end_time, period, steps, future_date):
    """Generates times between the end of the training period to the specified future date."""
    return pd.date_range(start = pd.Timestamp.fromordinal(end_time), end = future_date, freq = period).tolist()


def linear_regression(data, period, steps, future_date):
    """Creates a linear regression model for the share price along with a 95% confidence interval for the
    best-fit line."""
    y = format_data(data, period).dropna()
    times = [pd.Timestamp.toordinal(date) for date in y.index]
    start_time, end_time = times[0], times[-1]
    times = [time-start_time for time in times]
    future_times = generate_future_times(end_time, period, steps, future_date)
    future_times = [pd.Timestamp.toordinal(date) for date in future_times]
    future_times_from_times = [future_time-end_time+times[-1] for future_time in future_times]

    fitted_values, ci, pars, cov = compute_linear_confidence_interval(times, y["close"])
    predicted_values, predicted_ci = predict_linear_confidence_interval(future_times_from_times, pars, cov)
    ci_upper, ci_lower = fitted_values + ci, fitted_values - ci
    predicted_ci_upper, predicted_ci_lower = predicted_values + predicted_ci, predicted_values - predicted_ci

    #Computing correlation coefficient r.
    m, c, r, p, stderr = linregress(times, y["close"])
    rmse = compute_rmse(y["close"], fitted_values)

    times = [pd.Timestamp.fromordinal(time+start_time) for time in times]
    future_times = [pd.Timestamp.fromordinal(time) for time in future_times]

    return y, times, future_times, fitted_values, ci_upper, ci_lower, predicted_values, predicted_ci_upper, predicted_ci_lower, r, rmse

# https://towardsdatascience.com/an-end-to-end-project-on-time-series-analysis-and-forecasting-with-python-4835e6bf050b
def time_series_seasonal(data, period):
    """Creates a seasonal time series prediction (not called in the main function but could be used if needed)"""
    y = format_data(data, period)
    decomposition = sm.tsa.seasonal_decompose(y, model='additive')
    fig = decomposition.plot()
    plt.show()

def create_arima_forecast(data, period):
    """Creates the ARIMA time series model"""
    y = format_data(data, period)

    p = d = q = range(0, 2)
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

    aic_list = []
    params = []
    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                mod = sm.tsa.statespace.SARIMAX(y,order=param,seasonal_order=param_seasonal,enforce_stationarity=False,enforce_invertibility=False)
                results = mod.fit(disp=0)
                params.append([param, param_seasonal])
                aic_list.append(results.aic)
            except:
                continue
    optimal_params = params[aic_list.index(min(aic_list))]

    mod = sm.tsa.statespace.SARIMAX(y,order=optimal_params[0],seasonal_order=optimal_params[1],enforce_stationarity=False,enforce_invertibility=False)
    results = mod.fit(disp=0)
    return results

def time_series_training(results, y):
    """Creates a ARIMA predictions between the training period dates."""
    pred = results.get_prediction(start=y.index[0], dynamic=False)
    pred_ci = pred.conf_int()
    return pred, pred_ci

def time_series_forecast(results, steps, future_date):
    """Creates a ARIMA time series prediction for the specified date."""
    pred_uc = results.get_forecast(steps=future_date)
    pred_ci = pred_uc.conf_int()
    return pred_uc, pred_ci
