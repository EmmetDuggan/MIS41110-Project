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
    cols = data.columns
    data = data.drop([col for col in cols if col != "date" and col != "close"], axis = 1)
    data["date"] = pd.to_datetime(data["date"])
    return data.set_index("date").resample(period).mean()

def linear_fit(x, m, c):
    return x*m + c

def gradient_matrix(x):
    return np.array([[x],[1]])

def compute_linear_confidence_interval(x, y):
    pars, cov = curve_fit(linear_fit, x, y)
    fit_vals = np.array([linear_fit(z, *pars) for z in x])
    return fit_vals, np.sqrt(np.array([float(gradient_matrix(z).T @ cov @ gradient_matrix(z)) for z in x])), pars, cov

def predict_linear_confidence_interval(x, pars, cov):
    fit_vals = np.array([linear_fit(z, *pars) for z in x])
    return fit_vals, np.sqrt(np.array([float(gradient_matrix(z).T @ cov @ gradient_matrix(z)) for z in x]))

def generate_future_times(end_time, period, steps):
    if period == "d":
        return [end_time + i for i in range(steps)]
    else:
        return [end_time + i*30 for i in range(steps)]

# https://www.statsmodels.org/stable/examples/notebooks/generated/ols.html
def linear_regression(data, period, steps):
    y = format_data(data, period).dropna()
    times = [pd.Timestamp.toordinal(date) for date in y.index]
    start_time, end_time = times[0], times[-1]
    times = [time-start_time for time in times]
    future_times = generate_future_times(times[-1], period, steps)

    fitted_values, ci, pars, cov = compute_linear_confidence_interval(times, y["close"])
    predicted_values, predicted_ci = predict_linear_confidence_interval(future_times, pars, cov)
    ci_upper, ci_lower = fitted_values + ci, fitted_values - ci
    predicted_ci_upper, predicted_ci_lower = predicted_values + predicted_ci, predicted_values - predicted_ci

    times = [pd.Timestamp.fromordinal(time+start_time) for time in times]
    future_times = [pd.Timestamp.fromordinal(time+start_time) for time in future_times]

    return y, times, future_times, fitted_values, ci_upper, ci_lower, predicted_values, predicted_ci_upper, predicted_ci_lower


    # y = format_data(data, period)
    # times = [pd.Timestamp.toordinal(date) for date in y.index]
    # start_time = times[0]
    # times = [time-start_time for time in times]
    # mod = sm.OLS(times, y)
    #
    # res = mod.fit()
    # predicted_values = res.predict()
    # prstd, ci_low, ci_high = wls_prediction_std(res)
    # print(predicted_values)
    #
    # times = [pd.Timestamp.fromordinal(time+start_time) for time in times]
    # print(times)
    # #ax = y.plot(label='Observed')
    # plt.plot(times, y["close"], label="Data")
    # plt.plot(times, predicted_values, 'r-', label="OLS")
    # plt.plot(times, ci_high, 'r--')
    # plt.plot(times, ci_low, 'r--')
    # # ax.legend(loc='best')
    # print(res.summary())
    # plt.show()

def time_series_seasonal(data, period):
    y = format_data(data, period)
    decomposition = sm.tsa.seasonal_decompose(y, model='additive')
    fig = decomposition.plot()
    plt.show()

def create_arima_forecast(data, period):
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
    #print(results.summary().tables[1])
    return results

def time_series_training(data, period):
    y = format_data(data, period)
    results = create_arima_forecast(data, period)

    pred = results.get_prediction(start=y.index[round(-len(y)/4)], dynamic=False)
    pred_ci = pred.conf_int()
    ax = y.plot(label='Observed')
    pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))
    ax.fill_between(pred_ci.index,pred_ci.iloc[:, 0],pred_ci.iloc[:, 1], color='k', alpha=.2)
    ax.set_xlabel('Date (yyyy-mm-dd)')
    ax.set_ylabel('Stock Price ($)')
    plt.legend()
    plt.show()

def time_series_forecast(results, steps):

    pred_uc = results.get_forecast(steps=steps)
    pred_ci = pred_uc.conf_int()
    return pred_uc, pred_ci

    # ax = y.plot(label='Observed', figsize=(14, 7))
    # pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
    # ax.fill_between(pred_ci.index,pred_ci.iloc[:, 0],pred_ci.iloc[:, 1], color='k', alpha=.25)
    # ax.set_xlabel('Date (yyyy-mm-dd)')
    # ax.set_ylabel('Stock Price ($)')
    # plt.legend()
    # plt.show()

    # results.plot_diagnostics(figsize=(16, 8))
    # plt.show()
    #
    # pred = results.get_prediction(start=pd.to_datetime('2017-01-01'), dynamic=False)
    # pred_ci = pred.conf_int()
    # ax = y['2014':].plot(label='observed')
    # pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))
    # ax.fill_between(pred_ci.index,pred_ci.iloc[:, 0],pred_ci.iloc[:, 1], color='k', alpha=.2)
    # ax.set_xlabel('Date')
    # ax.set_ylabel('Furniture Sales')
    # plt.legend()
    # plt.show()



#################################################################################################################




def lin_fit_values(data, period):
    y = format_data(data, period)
    x = [datetime.datetime.timestamp(date) for date in data.index]
    pars, cov = curve_fit(linear_fit, x, data["close"])
    print(pars)
    print(cov)
    m, c = pars
    sigma_m, sigma_c = np.sqrt(cov[0][0]), np.sqrt(cov[1][1])
    linear_vals = [linear_fit(time, *pars) for time in x]
    #ci_upper = linear_vals + np.array([float(gradient_matrix(x,m,c).T * pcov *gradient_matrix(x,m,c)) for x in data.index])
    ax = y.plot(label='Observed')
    ax.plot(x, linear_vals, 'r-')
    #pred.predicted_mean.plot(ax=ax, label='Linear Fit', alpha=.7, figsize=(14, 7))
    #ax.fill_between(pred_ci.index,pred_ci.iloc[:, 0],pred_ci.iloc[:, 1], color='k', alpha=.2)
    ax.set_xlabel('Date (yyyy-mm-dd)')
    ax.set_ylabel('Stock Price ($)')
    plt.legend()
    plt.show()
