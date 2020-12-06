import unittest
from project_io import connect_to_api, access_archive
from project_frames import DataUnavailableException, MultiDataUnavailableException

class TestAPIData(unittest.TestCase):
    def test_connect_to_api_alphavantage(self):
        data = connect_to_api("alphavantage", "V", "NO7SX7BKV0TRLHAM", "2020-10-09", "2020-10-30")[0]
        self.assertTrue("{" not in data.keys())

    def test_connect_to_api_macrotrends(self):
        data = connect_to_api("macrotrends", "V", "NO7SX7BKV0TRLHAM", "2020-10-12", "2020-10-16")[0]
        self.assertEqual(len(data), 4)

    def test_connect_to_api_yahoo(self):
        data = connect_to_api("yahoo", "V", "NO7SX7BKV0TRLHAM", "2020-10-12", "2020-10-16")[0]
        self.assertEqual(len(data), 5)

    # def test_connect_to_api_nasdaq(self):
    #     data = connect_to_api("nasdaq", "AMZN", "NO7SX7BKV0TRLHAM", "2020-10-01", "2020-10-30")[0]
    #     self.assertEqual(len(data.columns), 6)

    def test_access_archive(self):
        data = access_archive("google_sample.csv", "goog", "date", "%d/%m/%Y")
        self.assertTrue(list(data.columns), ["date", "close", "volume", "open", "high", "low"])




class TestExceptions(unittest.TestCase):
    date_list = ["2020-10-20", "2020-10-21", "2020-10-22", "2020-10-23", "2020-10-24"]

    def check_if_in_list(self, date, ticker):
        if date not in self.date_list:
            raise DataUnavailableException(ticker, date)

    def test_single_exception_raise(self):
        date = "2020-10-01"
        ticker = "AAPL"

        try:
            self.check_if_in_list(date, ticker)
        except DataUnavailableException as e:
            self.assertTrue(e.message, "Data unavailable for \"AAPL\" for the date: 2020-10-01")

    def test_multiple_exception_raise(self):
        dates = ["2020-01-01", "2020-01-02", "2020-10-22"]
        tickers = ["AAPL", "MSFT", "FB"]
        exception_list = []

        for date, ticker in zip(dates, tickers):
            try:
                self.check_if_in_list(date, ticker)
            except DataUnavailableException as e:
                self.assertTrue(e.message, "Data unavailable for \"{}\" for the date: {}".format(ticker, date))
                exception_list.append(e)

        self.assertTrue(len(exception_list), 2)



if __name__ == '__main__':
    unittest.main()
