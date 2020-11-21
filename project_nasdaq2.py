import requests
import pandas as pd

#print("Starting")

def connect_to_nasdaq(ticker, name, sector):

    got_data = False
    while got_data == False:
        cookies = {
            'NSC_W.TJUFEFGFOEFS.OBTEBR.443': 'ffffffffc3a08e0e45525d5f4f58455e445a4a42378b',
            'AKA_A2': 'A',
            'ak_bmsc': 'A25CDF47767963B833D84021D7FEFFAF58DDDE492E3A000040BAB25F3009C36A~pluOgzuT2N+YNGZ5h/GRZBSKADiOnGjMeNKzYhPmfWShW6sBo39kcgJd7QoetQQTDmqDPtg3Stp1mdP4nGZFyjm69wS6eGW4ebeoX30gEnJVSs4vrifjlS5GGMeFxRjm/XnWyD+f6EdVwNzuqNlJdqxMA80eOM+w3HKv36q7s6WcAoVX40rlMzZVLmbhNIiDoT8EYVD8vvQUjW6ggqabet9oCRLkibH65oBp/K1K2Z8iY=',
            'c_enabled`$': 'true',
            'clientPrefs': '||||lightg',
            's_sess': '%20s_cc%3Dtrue%3B%20s_sq%3Dnasdaqprod%253D%252526pid%25253D' + name + '%25252520Common%25252520Stock%25252520%25252528MSFT%25252529%25252520Historical%25252520Prices%25252520%25252526%25252520Data%25252520-%25252520NASDAQ.com%252526pidt%25253D1%252526oid%25253Djavascript%2525253AgetQuotes%25252528true%25252529%2525253B%252526ot%25253DA%3B',
            's_pers': '%20bc%3D2%7C1605635030295%3B%20s_nr%3D1605548689645-New%7C1613324689645%3B',
            'rewrite': 'true',
            'bm_mi': '94DF1C47DCA7537A9EBC58FB35BDDE70~4V4QJY2t6A0oWUYaPV24SzQv2HN2Zbd0jHlNHqibKZuxkFSP4OXjIQcObeTIlc0hRiFZdel/7idzACVd5IDHiZeu1Zk072bspB3UJeJChS5IEZwDmEjyhQMN3P5+F8b1Ac6zo7qL5P2jCoS+QMqSG34pGEJKZkN1chZTyi6vuOlvrzCqiFa30pEPASjRy+2JAmtNdJA41rIDHl8bzVo3CsJ7Xb62zhiyoX2+b0PziyZkfyvr6jW26e6RQevDkceX',
            'bm_sv': 'D18EB42D7404C01A66DA545E24E50055~0E8TbzeX0ObZJhzhEwqtOmevzK4EP/WWBeSxRWVLYSlzIJXtb6jbmFpcpOI5QrFXm4RUBj7T8fI9StS1tpn+E7NqIsWqCPQ27YSOhl8g6VK80dDGcO5xoh+XCRL2/hqTIIWXWetxfr/EQKdEqG6du55zfzMaBL3YF29BlghTAvc=',
            'selectedsymboltype': ticker.upper() + '%2cCOMMON%20STOCK%2cNASDAQ-GS',
            'selectedsymbolindustry': ticker.upper() + ',' + sector.lower(),
            'userSymbolList': ticker.upper() + '+',
            'userCookiePref': 'true',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
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
          '__EVENTVALIDATION': 'i4VXdxqAZ7stnzXIB5GztXETgQzUSEnNa+NlSoz+DobaqW15UFYFDE27JOS4CAV1bKuNu18U1WUuLRuZ2IlsuCJFDfIIn1iszBXbLxaIUBKs0snc9N/dLWLuF10F3407',
          'ctl00$quotes_content_left$submitString': '10y|true|' + ticker.upper()
        }

        response = requests.post('https://old.nasdaq.com/symbol/' + ticker.lower() + '/historical', headers=headers, cookies=cookies, data=data)

        #Reading response data.
        d = response.text
        #Getting column names from response data.
        #col_names = str(d[0:43]).replace("\"", "").split(",")
        #print(col_names)
        #Removing quotation marks from response data.
        d = str(d).replace("\"", "").split()
        #Splitting each row in the response data.
        entries = [row.split(",") for row in d]
        #Removing initial row (which contains the headers) from the data.
        col_names = entries[0]

        if len(col_names) == 1:
            #raise ValueError
            print("Unable to get data. Retrying...")
            continue

        else:
            #Creating a DataFrame containing the response data.
            df = pd.DataFrame(entries[2:], columns = col_names)
            for column in df.columns:
                if column != "date":
                    #Changing the DataFrame entries from stings to floats where appropriate.
                    df[column] = df[column].astype(float)
                else:
                    df[column] = df[column].str.replace("/", "-")

            got_data = True
            return df

        # except ValueError:
        #     print("Unable to get data. Retrying...")
        #     continue
