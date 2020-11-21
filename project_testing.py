import unittest
from project_io import connect_to_api

class TestAPIData(unittest.TestCase):
    def test_connect_to_api_alphavantage(self):
        data = connect_to_api("alphavantage", "V", "NO7SX7BKV0TRLHAM", "2020-10-09", "2020-10-30")[0]
        self.assertTrue("{" not in data.keys())

    def test_connect_to_api_macrotrends(self):
        data = connect_to_api("macrotrends", "V", "NO7SX7BKV0TRLHAM", "2020-10-12", "2020-10-16")[0]
        self.assertEqual(len(data), 4)

if __name__ == '__main__':
    unittest.main()
