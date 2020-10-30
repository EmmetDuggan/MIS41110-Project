from project_io import read_file, connect_to_api

print(read_file("project_companies.csv"))
print(connect_to_api(input("Enter the service name: >"), "IBM", "demo"))
# print(connect_to_api("IBM", "demo"))
# print(connect_to_api("IBM", "demo")[200])
