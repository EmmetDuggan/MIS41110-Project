from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import print, box
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.measure import Measurement
import itertools
import sys
import time

def loading_symbol(finished):
    """Loading symbol function which does not quite work yet with threading."""
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if finished:
            break
        sys.stdout.write('\rPerforming predictive analysis...  ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    return

class TextInterface(Console):

    def __init__(self):
        """Initialises a Console object from the Rich library."""
        self.c = Console()

    def show_markdown(self):
        """Prints a markdown cell to the terminal, introducing the application."""
        with open('intro_markdown.txt') as intro:
            markdown = Markdown(intro.read())
        self.c.print(markdown)

    def ask_api(self):
        """Prints information about which APIs are available and ask the user to select an API
        or use an archive based on their preference."""
        self.c.print("")
        self.c.print(Panel("Enter the API from which data is to be drawn.\nIf you wish to query a downloaded database, enter \"Archive\" instead.", title = "API Selection"), justify = 'center')
        services = ["AlphaVantage", "MacroTrends", "Yahoo", "NASDAQ", "Archive"]
        options = [service.lower() for service in services]
        service_name = Prompt.ask("\nAPIs: \"AlphaVantage\", \"MacroTrends\", \"Yahoo! Finance\", \"NASDAQ\".\nInput options:", choices = options)
        return service_name

    def ask_single_or_multiple(self):
        """Asks the user whether they want to analyse the stocks of just one or multiple companies."""
        self.c.print("")
        self.c.print(Panel("Analyse data from multiple companies or a single company.\nNote that if using an archive database, only a single company may be analysed.\nTo produce graphs which are easily read, it is suggested to limit the number of companies to no more than 4.", title = "Number of Companies"), justify='center')
        options = ["1", "2"]
        number = Prompt.ask("Enter \"1\" for a single company. Enter \"2\" for two or more companies.\nInput options:", choices = options)
        return number

    def ask_tickers_or_names(self):
        """Asks the user if they want to query stocks by company ticker or name."""
        self.c.print("")
        self.c.print(Panel("Companies can be queried by ticker or name.\nTo search by ticker, enter \"t\" followed by the list of tickers, with each ticker separated by a semi-colon (;).\nTo search by name, enter \"n\" and each company name (in full), separating each with a semi-colon.", title = "Company Tickers & Names"), justify='center')
        options = ["t", "n"]
        ticker_name = Prompt.ask("Enter \"t\" to search by ticker. Enter \"n\" to search by name.\nInput options:", choices = options)
        if ticker_name == "t":
            companies_input = Prompt.ask("Enter the company tickers")
        else:
            companies_input = Prompt.ask("Enter the full company names")
        return ticker_name, companies_input

    def ask_dates(self):
        """Prints information about how dates should be entered and asks the user over which
        time period the model is to be trained."""
        self.c.print("")
        self.c.print(Panel("Enter the time period over which stock prices are to be analysed, and then the future date for which the stock price is to be calculated.\
        \nThe prediction tools will use this period to predict the stock prices at the specified future date.\
        \nThe model can be trained using either daily stock prices or from resampling the daily prices as the mean of the price for each month.\
        \nNote that AlphaVantage data is limited to 100 days; as such, the model can only be trained using daily data.\
        \nAlso note that resampled values are assigned dates relating to the start of each month.", title = "Time Period"), justify='center')
        options = ["d","m"]
        period_choice = Prompt.ask("Enter \"d\" if the model is to be trained using daily stock data or \"m\" if monthly stock data should be used.\nInput options:", choices = options)
        return period_choice

    def show_descriptive_stats(self, stats_frame):
        """Print a table of the descriptive statistics to the terminal. Does not quite work and so
        is not called in main function."""
        table = Table()
        table.add_column("Ticker")
        for company in stats_frame.columns:
            table.add_column(company)
            #
            # vals = []
            # for stat in stats_frame.index:
            #     stat_values = stats_frame.loc[stat][company].astype(str)
            #     for val in stat_values:
            #         vals.append(val)
            #     table.add_row(stat, [vals[i] for i in range(len(vals))])
        table.caption = "Descriptive statistics for each company."
        self.c.print(table)


    def ask_archive_date_format(self):
        self.c.print("")
        self.c.print(Panel("The format of dates in the archive file, as well as the column name in the file where dates are recorded,\
        \nare required to read the data from the archive.", title = "Archive Format"), justify='center')
        options = ["%d/%m/%Y","%m/%d/%Y","%Y/%m/%d", "%Y/%d/%m"]
        date_format = Prompt.ask("Enter the date format used in the archive. Archive dates must either be in the format \"%d/%m/%Y\", \"%Y/%m/%d\", \"%d-%m-%Y\" or \"%Y-%m-%d\". >")
        date_column_name = Prompt.ask("Enter the column name where dates are recorded in the archive")
        return date_format, date_column_name

    def export_data(self, data_to_save, plot_to_save):
        """Asks the user if they wish to export the results."""
        self.c.print("")
        self.c.print(Panel("The results of the predictive analysis can be exported.\nThe descriptive statistics can be saved to a CSV file, while the ARIMA forecast plot can be saved in PDF format.",
        title = "Export Results"), justify='center')
        options = ["y","n"]
        ans = Prompt.ask("Would you like to export the results?\nInput options:", choices = options)

        if ans == "y":
            name = input("Enter the file name to which the results are to be saved.\nNote that the CSV and PDF files will be of the same name. >")
            data_to_save.to_csv(name + ".csv")
            plot_to_save.savefig(name + ".pdf")
            self.c.print("Results exported successfully.")

    def close_interface(self):
        """Prints a closing message and ends the programme."""
        self.c.print(Panel("Thank you for using the Price Predictor application!\nWe hope you found it useful.\nEnjoy the rest of your day!"), justify='center')
