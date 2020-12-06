import requests
import pandas as pd

def connect_to_nasdaq(ticker, name, sector):
    """Connects to the NASDAQ historical stock records for a given ticker company.
    The sector is also required as the NASDAQ API cookies require the company sector to be inputted
    in order to retrieve data."""
    got_data = False
    count = 1
    while got_data == False and count <= 5:
        try:
            cookies = {
                'NSC_W.TJUFEFGFOEFS.OBTEBR.443': 'ffffffffc3a08e3345525d5f4f58455e445a4a42378b',
                'ak_bmsc': 'CFFF04C57CB0B2E3E945C30BDF63096058DDDE49B1550000210FCD5F27869556~plW+3zuUjgvseSHa8BqeUxADOup6k7oqWoi4kwKrnj36PUgNIa9U7FtLaKzEuC/FfFuIglwQGEDnjJDFKixiigVbHCeHEVKEy1nneSv1hb4H6YP7aeRo36OC2FBMEkzd3+893IySSn0XKmHgvDNwLL70X4pr2WSTmSL9HuMEShyNx6vZ7/QYXZSM6XvSX12Tc462w5yjLChbjrlQod8MIysWJHJ87F2TIb5yoeQW8G1OE=',
                'c_enabled`$': 'true',
                'clientPrefs': '||||lightg',
                's_sess': '%20s_cc%3Dtrue%3B%20s_sq%3Dnasdaqprod%253D%252526pid%25253D%25252528' + ticker.upper() + '%25252529%25252520Historical%25252520Prices%25252520%25252526%25252520Data%25252520-%25252520NASDAQ.com%252526pidt%25253D1%252526oid%25253Djavascript%2525253AgetQuotes%25252528true%25252529%2525253B%252526ot%25253DA%3B',
                's_pers': '%20bc%3D2%7C1607360683469%3B%20s_nr%3D1607274311531-New%7C1615050311531%3B',
                'rewrite': 'true',
                'bm_mi': '47D16960ECEF02160F0D6F280E2DE666~CmtyvRgq+zz0W7zwMgdkw2zNkHImxGUT05iRP4EiDhGwUGAseCHFWjCUaLutZnb7yZbxWaPE5bP6m4GszQ3t5F8uWM9webQbCF5KGwRGVUmLtmC7xnM4UxdH84xu4bFaQH9/rvVkETWFDlIWRUXSu+esCIPFZFewA5fDYAUJrRfd2QII96TuYoawgP3S9cmZ84siDZj5nZhx9QOsYG8Bc4nqQ5mZu3eC9eRgxBG+cNKQk/S5z62R137rUT7yn57V',
                'bm_sv': '72A4D60298D33CBE941BA34D9B1C7E10~vLmqG7pFOwp7l7S8A2HwaJHKQv6f/YkQ+o+LzTWjeteEgO2UVL3m2tpLPqVAIj6s9VZH6gNyRbHVefoi2cwXvH26SHFqBg++YcB28OR5X/vd1BMtQoTWscQc0qE9bAD9IsWXSIlfOpttnsfdmuuPoXXYd7drohCrUii/SMq6yMI=',
                'selectedsymboltype': ticker.upper() + '%2cCOMMON%20STOCK%2cNASDAQ-GS',
                'selectedsymbolindustry': ticker.upper() + ',' + sector.lower(),
                'userSymbolList': ticker.upper() + '+',
                'userCookiePref': 'true',
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://old.nasdaq.com',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Referer': 'https://old.nasdaq.com/symbol/' + ticker.lower() + '/historical',
                'Upgrade-Insecure-Requests': '1',
                'TE': 'Trailers',
            }

            data = {
              '__VIEWSTATE': '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',
              '__VIEWSTATEGENERATOR': '87BE3BDB',
              '__VIEWSTATEENCRYPTED': '',
              '__EVENTVALIDATION': 'A2K84VcrQIvlHN6KYicJMV53tdVLrHb18GFgyjjZ/jZwnHBrRSLsSvWkMIxlYlAkySS11uWGdQEKD5auZ8JNWGqRQcn1FUX4EOa8GVZGzfqPWHKYgwMda0jV204It7bC',
              'ctl00$quotes_content_left$submitString': '10y|true|' + ticker.upper()
            }

            response = requests.post('https://old.nasdaq.com/symbol/' + ticker.lower() + '/historical', headers=headers, cookies=cookies, data=data)
            #Reading response data.
            d = response.text
            #Removing quotation marks from response data.
            d = str(d).replace("\"", "").split()
            #Splitting each row in the response data.
            entries = [row.split(",") for row in d]
            #Removing initial row (which contains the headers) from the data.
            col_names = entries[0]
            #Creating a DataFrame containing the response data.
            df = pd.DataFrame(entries[1:], columns = col_names)
            for column in df.columns:
                if column != "date":
                    #Changing the DataFrame entries from stings to floats where appropriate.
                    df[column] = df[column].astype(float)
                else:
                    df[column] = df[column].str.replace("/", "-")

            got_data = True
            return df

        except ValueError:
            count += 1
            print("Unable to access the NASDAQ API. Retrying...")
            continue
