class DataUnavailableException(Exception):
    """Custom exception class. Raised if a particular company's records do not go back
    as far as the user wants, but the records of the first company entered by the user does."""
    ticker = ""
    date = ""
    def __init__(self, ticker, date):
            self.message = "Data unavailable for \"" + ticker + "\" for the date: " + date
            self.ticker = ticker
            self.date = date
            super().__init__(self.message)

class MultiDataUnavailableException(Exception):
    """Custom exception class. Bundles several DataUnavailableExceptions into a single exception
    which is raised when the records of multiple companies do not go back as far as the user wants."""
    exceptions = []
    tickers = []
    def __init__(self):
        self.message = "Multiple companies have limited data."
        super().__init__(self.message)

    def add_exception(self, exception, ticker):
        self.exceptions.append(exception)
        self.tickers.append(ticker)

class InvalidTickerException(Exception):
    """Custom exception class. Raised if the entered ticker is not found."""
    ticker = ""
    def __init__(self, ticker):
        self.message = "The ticker " + ticker + " was not found in the database.\nPlease re-enter the company tickers."
        self.ticker = ticker
        super().__init__(self.message)
