import datetime
from datetime import timedelta

#Function to convert user input dates to integers.
def date_in_to_integers(date):
    date_year, date_month, date_day = date.split("-")
    date_year, date_month, date_day = int(date_year), int(date_month), int(date_day)
    return date_year, date_month, date_day

#Function to convert date in integer format to string.
def date_to_string_hyphen(date_year, date_month, date_day):
    if date_month < 10:
        date_month = "0" + str(date_month)
    if date_day < 10:
        date_day = "0" + str(date_day)
    return str(date_year) + "-" + str(date_month) + "-" + str(date_day)

#Function to obtain valid dates from the user for which company performance
#can be analysed.
def get_valid_dates():
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

#Function is get the closest dates to the ones entered via index.
def get_date_options(dts, dt_differences):
    minimum_index = dt_differences.index(min(dt_differences))
    try:
        return [datetime.datetime.strftime(dts[minimum_index], '%Y-%m-%d'),
        datetime.datetime.strftime(dts[minimum_index+1], '%Y-%m-%d')]
    except IndexError:
        return [datetime.datetime.strftime(dts[minimum_index], '%Y-%m-%d'),
        datetime.datetime.strftime(dts[minimum_index-1], '%Y-%m-%d')]

#Function to ask the user for which of the available dates they would like
#to analyse.
def ask_for_date_selection(unavailable_date, date_options):
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

#https://www.dataquest.io/blog/python-datetime-tutorial/
#Function to find the nearest dates to those entered for which data exists.
def find_nearest_date(data_dates, start_date, end_date, gui = False):
    start_date_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    data_dts = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in data_dates]


    if start_date_dt in data_dts and end_date_dt in data_dts:
        return start_date, end_date

    elif start_date_dt not in data_dts and end_date_dt in data_dts:
        dt_differences = [abs(dt - start_date_dt) for dt in data_dts]
        options = get_date_options(data_dts, dt_differences)
        if gui == False:
            new_start = ask_for_date_selection(start_date, options)
            return new_start, end_date
        else:
            return False, end_date, options

    elif start_date_dt in data_dts and end_date_dt not in data_dts:
        dt_differences = [abs(dt - end_date_dt) for dt in data_dts]
        options = get_date_options(data_dts, dt_differences)
        if gui == False:
            new_end = ask_for_date_selection(end_date, options)
            return start_date, new_end
        else:
            return start_date, False, options

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
