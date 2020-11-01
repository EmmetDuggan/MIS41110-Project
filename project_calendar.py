import datetime
from datetime import timedelta


def date_in_to_integers(date):
    date_year, date_month, date_day = date.split("-")
    date_year, date_month, date_day = int(date_year), int(date_month), int(date_day)
    return date_year, date_month, date_day

def date_to_string_hyphen(date_year, date_month, date_day):
    if date_month < 10:
        date_month = "0" + str(date_month)
    if date_day < 10:
        date_day = "0" + str(date_day)
    return str(date_year) + "-" + str(date_month) + "-" + str(date_day)

def get_valid_dates():
    date_today = datetime.datetime.today()
    start_date_formatted = ""
    end_date_formatted = ""
    while True:
        start_date = input("Enter a start date (yyyy-mm-dd): >")
        end_date = input("Enter an end date (yyyy-mm-dd): >")

        try:
            s_year, s_month, s_day = start_date.split("-")
            e_year, e_month, e_day = end_date.split("-")

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
