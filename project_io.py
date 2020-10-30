import pandas as pd
import urllib.request
from io import StringIO

def read_file(filename):
    return pd.DataFrame(pd.read_csv(filename))

def get_api_data(api_url):
    with urllib.request.urlopen(api_url) as response:
        data = str(response.read(), 'utf-8')
        data_string = StringIO(data)
        return pd.DataFrame(pd.read_csv(data_string))



# https://stackoverflow.com/questions/47379476/how-to-convert-bytes-data-into-a-python-pandas-dataframe
def connect_to_api(service_name, symbol_name, api_key):
    api_list = ["alphavantage", "financial content"]
    service_name = service_name.lower()
    if service_name in api_list:
        if service_name == api_list[0]:
            return get_api_data("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + symbol_name + "&apikey=" + api_key + "&datatype=csv")
        elif service_name == api_list[1]:
            return service_name
    else:
        print("Please enter a valid API:",api_list)
