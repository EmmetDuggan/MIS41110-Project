from project_io import connect_to_api
from project_calendar import get_valid_dates, find_nearest_date

start_date = input("Enter start date:")
end_date = input("Enter end date:")
data, date_column_name, reverse_data = connect_to_api("alphavantage", "V", "NO7SX7BKV0TRLHAM", start_date, end_date)

#print(data[date_column_name])
#find_nearest_date(data[date_column_name], start_date, end_date)
