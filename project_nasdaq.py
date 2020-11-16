import requests
import pandas as pd

def connect_to_nasdaq(ticker, name, sector):

    got_data = False
    while got_data == False:
        try:
            cookies = {
                'selectedsymboltype': ticker.upper() + '%2cCOMMON%20STOCK%2cNASDAQ-GS',
                'selectedsymbolindustry': ticker.upper() + ',' + sector.lower(),
                'NSC_W.TJUFEFGFOEFS.OBTEBR.443': 'ffffffffc3a0f73345525d5f4f58455e445a4a42378b',
                'ak_bmsc': '5262E1508DD4BBB9CEAA9FE0227BDC6C58DDDE492E3A00008EE5AE5F6FA3926A~plCZYQ830u+RHic80lNjzBJNDxhcF56er6iPm72r1YNpp/aj5Y0RSER474c8wCUBZinC5Ww+J3N1BII3WzAvEAfLUHsKDFyZ2rIRocrj1gsUrt2ClLvOLxRMlv1drFPCJ2KgxmFCCPl3XEQCUfnVMatsKv4elCaMvO2dWNMe4Xc/ypfSVX3Y907G/OBlxH7r3ibX7h0C206HxPS4fJYcVYnOjttd8ApPMKC/Nd44ljw04=',
                'c_enabled`$': 'true',
                'clientPrefs': '||||lightg',
                's_sess': '%20s_cc%3Dtrue%3B%20s_sq%3Dnasdaqprod%253D%252526pid%25253D' + name + '%2525252C%25252520Inc.%25252520Common%25252520Stock%25252520%25252528' + ticker.upper() + '%25252529%25252520Historical%25252520Prices%25252520%25252526%25252520Data%25252520-%25252520NASDAQ.com%252526pidt%25253D1%252526oid%25253Djavascript%2525253AgetQuotes%25252528true%25252529%2525253B%252526ot%25253DA%3B',
                's_pers': '%20bc%3D2%7C1605383967021%3B%20s_nr%3D1605297687695-New%7C1613073687695%3B',
                'userSymbolList': ticker.upper() + '+&VCVC',
                'userCookiePref': 'true',
                'bm_mi': '835C2225803BA7638626A3A86A76C876~4V4QJY2t6A0oWUYaPV24S+zGs0HfaWZf/Icpuc7DwhYqCBx90YNFXPFDzPHTc9fMudHwJ0UfDEDSfJ945l6gOZAECh31VVE9S0wHPAgVI0TbKK1P7C3whYZcR8esFufRg1B46jqR97VIUfW7bt49pozoJH77ReSzWyUNtm+FxuEXyVuPE/Zu3/38CCAGYnJNT+4yrBS1FchdZn1Fj1oYSSAi/gfLbJY6q4aBAbzXIEPbx+JhB1mBK72PSClVvP+0',
                'bm_sv': '4196092574D5DB64FB6E0A533252C339~0E8TbzeX0ObZJhzhEwqtOs4B7eyWb9QExhpsKfB7GL4PZJKQloqKtuIzyUucnwKKpuen6WarvSBubGQYIHEsXHB6UeQTj4urrnN+Ngu/u3ftB3ELHvlihTgrYuBZawLJgMnC8y1wFRfJnc8hJgToAg==',
                'AKA_A2': 'A',
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
            }

            data = {
              '__VIEWSTATE': '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',
              '__VIEWSTATEGENERATOR': '87BE3BDB',
              '__VIEWSTATEENCRYPTED': '',
              '__EVENTVALIDATION': 'SghiJ7CXRkHfZBRHLe2zIT8AotqaF2T1QayV2KXrtYmpMzCw+1aUlx0DNJNmN4tQRWHPbP05zU1v17AwflrxP24ssDLHP66c3PoVpERDxfL8tPUWEOwApkzuu68G58Jp',
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
            continue


data = connect_to_nasdaq('NDAQ', 'Nasdaq', 'finance')
print(data)





#connect_to_nasdaq('AAPL', 'Apple%25252520Inc.', 'technology')
#print("Apple Data^")









#import requests

cookies = {
    'selectedsymboltype': 'AAPL%2cCOMMON%20STOCK%2cNASDAQ-GS',
    'selectedsymbolindustry': 'AAPL,technology',
    'NSC_W.TJUFEFGFOEFS.OBTEBR.443': 'ffffffffc3a08e3345525d5f4f58455e445a4a42378b',
    'ak_bmsc': '5262E1508DD4BBB9CEAA9FE0227BDC6C58DDDE492E3A00008EE5AE5F6FA3926A~ply2i9Th7vxBlfwVN2NNTfnovrneufMnK8Of3GnCv5v9EhKqsDFHaHoFK06DiyEusejjNNC08r+DSn2fcmgCKgzfqePKOFtnmiHCQw+J7sUlS48Yw9YJWfikwroGOKIO9gE5o64d/kv2npXeIzhuvw1TpZLhbI3nrUHcnNoxYCSxIzldq2fN7pU46vcDrU9ets6rweUelOjP1EVxPWUUpJwoUz6+ziot+P2poaMtp5yzH88cTR67Mv4EL5ySCfhVC9RtPuvfnSY2CH3N6BrW+ZnRHHaRbYq6HjM9pN5UeaDx0=',
    'c_enabled`$': 'true',
    'clientPrefs': '||||lightg',
    's_sess': '%20s_cc%3Dtrue%3B%20s_sq%3Dnasdaqprod%253D%252526pid%25253DApple%25252520Inc.%25252520Common%25252520Stock%25252520%25252528AAPL%25252529%25252520Historical%25252520Prices%25252520%25252526%25252520Data%25252520-%25252520NASDAQ.com%252526pidt%25253D1%252526oid%25253Djavascript%2525253AgetQuotes%25252528true%25252529%2525253B%252526ot%25253DA%3B',
    's_pers': '%20bc%3D2%7C1605383967021%3B%20s_nr%3D1605298390814-New%7C1613074390814%3B',
    'userSymbolList': 'AAPL+&NDAQ&VCVC',
    'userCookiePref': 'true',
    'bm_mi': '835C2225803BA7638626A3A86A76C876~4V4QJY2t6A0oWUYaPV24S+zGs0HfaWZf/Icpuc7DwhYqCBx90YNFXPFDzPHTc9fM5eB6oKk8hz1fgefUs7yvlbAKGKOKOknmpuuNSaVWKBgDdnnzV2ecSgOllZ11ZJ5eoT7Qyn1an3R8eY04V64E1KAPgFxaN0QqShjuR9KWunX+cXrX/r31YCWU2i0yToMkx2HXqAlWRhclK605NB/zl9BnTymFzJOg5oNS6cuFyqysU/CkZp3rjd8W5Ge4AwUW',
    'bm_sv': '4196092574D5DB64FB6E0A533252C339~0E8TbzeX0ObZJhzhEwqtOs4B7eyWb9QExhpsKfB7GL4PZJKQloqKtuIzyUucnwKKpuen6WarvSBubGQYIHEsXHB6UeQTj4urrnN+Ngu/u3fG3ec8Kz0yt5hzAI3ji7HAoUbEz3yJZBqKBQ9K+4XR2vFAUkMu8vzi/7VvEIuXUt8=',
    'AKA_A2': 'A',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://old.nasdaq.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://old.nasdaq.com/symbol/aapl/historical',
    'Upgrade-Insecure-Requests': '1',
    'TE': 'Trailers',
}

data = {
  '__VIEWSTATE': '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',
  '__VIEWSTATEGENERATOR': '87BE3BDB',
  '__VIEWSTATEENCRYPTED': '',
  '__EVENTVALIDATION': 'Dx30PmjTgkLm5s6gH436cysaaUzfqkzP/v7X0/u9eV5WhxNscizkG1o6TdUSKA0FcmeJmuTcC9UW2Prt6j8s53SB0ctAcOgLOKuftiMkgn5gdXhZyoeAq05Xi7/ymnp6',
  'ctl00$quotes_content_left$submitString': '10y|true|AAPL'
}

response = requests.post('https://old.nasdaq.com/symbol/aapl/historical', headers=headers, cookies=cookies, data=data)
