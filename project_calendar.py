import datetime
import numpy as np
import pandas as pd
from datetime import timedelta

def date_in_to_integers(date):
    """Converts user input dates to integers."""
    date_year, date_month, date_day = date.split("-")
    date_year, date_month, date_day = int(date_year), int(date_month), int(date_day)
    return date_year, date_month, date_day

def date_to_string_hyphen(date_year, date_month, date_day):
    """Reformats the date into the form yyyy-mm-dd."""
    if date_month < 10:
        date_month = "0" + str(date_month)
    if date_day < 10:
        date_day = "0" + str(date_day)
    return str(date_year) + "-" + str(date_month) + "-" + str(date_day)

def get_valid_dates():
    """Obtain valid dates from the user for which company data can be analysed."""
    date_today = datetime.datetime.today()
    start_date_formatted = ""
    end_date_formatted = ""
    while True:
        start_date = input("Enter a start date (yyyy-mm-dd): >")
        end_date = input("Enter an end date (yyyy-mm-dd): >")

        #If dates are not in correct format, a ValueError is raised.
        try:
            s_year, s_month, s_day = start_date.split("-")
            e_year, e_month, e_day = end_date.split("-")

            #Components of dates are converted into integers to check
            #that end date is preceeded by start date.
            s_year, s_month, s_day = date_in_to_integers(start_date)
            e_year, e_month, e_day = date_in_to_integers(end_date)

            s = datetime.datetime(s_year, s_month, s_day)
            e = datetime.datetime(e_year, e_month, e_day)
            if timedelta.total_seconds(s - e) > 0 or timedelta.total_seconds(s - date_today) > 0 or timedelta.total_seconds(e - date_today) > 0:
                raise ValueError
            start_date_formatted = date_to_string_hyphen(s_year, s_month, s_day)
            end_date_formatted = date_to_string_hyphen(e_year, e_month, e_day)
            break

        except ValueError:
            print("The dates entered are invalid. \nEnter dates in the form yyyy-mm-dd. Start date must precede end date.")
    return [start_date_formatted, end_date_formatted]

def validate_future_date(future_date):
    """Validates the format of the future date specified and ensures it is in the future."""
    time_now = datetime.datetime.now()
    while True:
        try:
            year, month, day = future_date.split("-")
            year, month, day = date_in_to_integers(future_date)
            f = datetime.datetime(year, month, day)
            future_date_formatted = date_to_string_hyphen(year, month, day)

            if timedelta.total_seconds(f - time_now) < 0:
                raise ValueError
            break
        except ValueError:
            print("The future date entered are invalid. \nEnter dates in the form yyyy-mm-dd. The date must be in the future.")
            future_date = input("Please re-enter the date for which a prediction is required: >")
    return future_date_formatted

def get_date_options(dts, dt_differences):
    """Gets the closest dates to those entered using the indices of the dates in the data."""
    minimum_index = dt_differences.index(min(dt_differences))
    try:
        return [datetime.datetime.strftime(dts[minimum_index], '%Y-%m-%d'),
        datetime.datetime.strftime(dts[minimum_index+1], '%Y-%m-%d')]
    except IndexError:
        return [datetime.datetime.strftime(dts[minimum_index], '%Y-%m-%d'),
        datetime.datetime.strftime(dts[minimum_index-1], '%Y-%m-%d')]

def ask_for_date_selection(unavailable_date, date_options):
    """Asks the user for which of the available dates they would like to analyse if data doesn't exist
    for the entered dates."""
    print("Unfortunately, no data is available for the date", unavailable_date, ". The closest dates are:", date_options)
    selection = input("Please select one of the dates for which data is available: >")
    while True:
        try:
            if selection in date_options:
                return selection
                break
            else:
                raise NameError
        except NameError:
            print("Enter only one of the available dates in the form yyyy-mm-dd.")
            selection =input("Please select one of the dates for which data is available: >")

def find_nearest_date(data_dts, start_date, end_date, gui = False):
    """Finds the nearest date in the data set for which data exists if data for the inputted
    dates is not found."""
    if not isinstance(start_date, datetime.date):
        start_date_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        start_date_dt = start_date
        end_date_dt = end_date

    #If both the start and end dates are in the data set, the dates are returned.
    if start_date_dt in data_dts and end_date_dt in data_dts:
        return start_date, end_date

    #If only the start date is not found, the nearest date to the start date for which data exists
    #is found.
    elif start_date_dt not in data_dts and end_date_dt in data_dts:
        dt_differences = [abs(dt - start_date_dt) for dt in data_dts]
        options = get_date_options(data_dts, dt_differences)
        if gui == False:
            new_start = ask_for_date_selection(start_date, options)
            return new_start, end_date
        else:
            return False, end_date, options

    #If only the end date is not found, the nearest date to the end date for which data exists
    #is found.
    elif start_date_dt in data_dts and end_date_dt not in data_dts:
        dt_differences = [abs(dt - end_date_dt) for dt in data_dts]
        options = get_date_options(data_dts, dt_differences)
        if gui == False:
            new_end = ask_for_date_selection(end_date, options)
            return start_date, new_end
        else:
            return start_date, False, options

    #If both the start and end dates are not found, the nearest dates for both the start and end
    #date for which data exists is found.
    elif start_date_dt not in data_dts and end_date_dt not in data_dts:
        start_dt_differences = [abs(dt - start_date_dt) for dt in data_dts]
        end_dt_differences = [abs(dt - end_date_dt) for dt in data_dts]
        start_options = get_date_options(data_dts, start_dt_differences)
        end_options = get_date_options(data_dts, end_dt_differences)
        if gui == False:
            new_start = ask_for_date_selection(start_date, start_options)
            new_end = ask_for_date_selection(end_date, end_options)
            return new_start, new_end
        else:
            return False, False, start_options, end_options
