from project_io import read_file, connect_to_api
from project_data_visualisation import time_series
from project_descriptive_stats import compute_descriptive_stats, make_stats_frame, add_to_frame

#print(connect_to_api(input("Enter the service name: >"), "IBM", "demo"))
data, date_column_name, reverse_data = connect_to_api(input("Enter the service name: >"), "IBM", "NO7SX7BKV0TRLHAM")
stats = compute_descriptive_stats(data["open"])
stats_frame = make_stats_frame(stats, "IBM")

data, date_column_name, reverse_data = connect_to_api(input("Enter the service name: >"), "V", "NO7SX7BKV0TRLHAM")
stats = compute_descriptive_stats(data["open"])
add_to_frame(stats, "V", stats_frame)
print(stats_frame)

time_series(data, date_column_name, reverse_data)
