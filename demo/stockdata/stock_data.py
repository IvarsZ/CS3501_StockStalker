from bs4 import BeautifulSoup
import csv, json, urllib, datetime, yql
from yql import YQLError
from django.utils.html import strip_tags

# url for querying historical stock data from yahoo finance.
YF_HISTORY_URL = 'http://ichart.finance.yahoo.com/table.csv?'

# list of accepted frequencies - d is daily, w is weekly, m is monthly.
VALID_FREQUENCIES = ['d', 'w', 'm']

'''
Thrown when no data were received from external data source,
usually caused by non existing ticker ticker or some error in the data source.
'''
class DataNotFoundException(Exception):
    pass

'''
Thrown when there is error with dates.
'''
class InvalidDatesException(Exception):
	pass
	
'''
Thrown when there is error with frequency.
'''
class InvalidFrequencyException(Exception):
	pass

'''
Gets a list with historical pricing information from Yahoo Finance.

ticker (string) - ticker of the stock company whose information is retrieved.
startDate (datetime.date object) - starting date to retrieve the information from (inclusive).
endDate (datetime.date object) - end date to retrieve the information till (inclusive).
frequency (char) - returns daily information if it is 'd', weekly if 'w', monthly if 'm'

returns - a list of dictionaries, each dictionary has the date of the day, volumne, and opening/closing and high/low stock price for that day.

If Yahoo finance returned an error (i.e. the ticker did not exist in Yahoo Finance) throws DataNotFoundlException.
If the end date is before the start date throws InvalidDatesException.
If the end date is after the current date throws InvalidDatesException.
If the frequency is not 'd', 'w' nor 'm' throws InvalidFrequencyException.
'''
def get_historical(ticker, startDate, endDate, frequency):

	# Checks that the dates.
	if (endDate < startDate):
		raise InvalidDatesException("The start date is after the end date")
		
	if (endDate > datetime.date.today()):
		raise InvalidDatesException("The end date is after the current date")
	
	# Checks the frequency.
	if (not frequency in VALID_FREQUENCIES):
		raise InvalidFrequencyException("The frequency " + frequency + " is not valid - " + ' '.join(VALID_FREQUENCIES))

	query = urllib.urlencode({'s': ticker, 'd': endDate.month - 1, 'e' : endDate.day, 'f' : endDate.year, 'g' : frequency, 'a' : startDate.month - 1, 'b' : startDate.day, 'c' : startDate.year})
	
	response = urllib.urlopen(YF_HISTORY_URL + query)
	
	# Checks that the csv file was successfully retrieved (ticker exists).
	if (response.info().getsubtype() != 'csv'):
		raise DataNotFoundException("ticker " + ticker + " was not found")

	# Reads the csv file into a dictionary with the required fields.
	csvFile = response.read()
	reader = csv.DictReader(csvFile.splitlines(), ['date', 'opening', 'high', 'low', 'closing', 'volume'])
	
	# Skips the first line with column names.
	reader.next()
	
	# Creates a list of the dictionaries and removes the extra keys.
	pricings = []
	for row in reader:
		row.pop(None, 'No Extra Keys')
		pricings.append(row)

	return pricings

'''
For a list of stock tickers, generate a corresponding list of dictionaries,
each of which represents the (near-real-time) current state of the stock. 
'''
def get_current(tickers):
	
	# Builds a string listing all tickers in the query format.
    tickerString = ','.join(['"'+str(sym)+'"' for sym in tickers])
    print(tickerString)

	# The query to get the stock information TODO with...
    query = 'select * from yahoo.finance.quotes where symbol in (' + tickerString + ')'
	
	# Uses python-yql library to publicly connect to Yahoo API and execute the query.
    y = yql.Public()

    try:
        result = y.execute(query, env = "http://datatables.org/alltables.env")
    except YQLError:
        return []

    stocks = []
    
    # Handle empty result set
    if result['query']['count'] < 1:
        return stocks

    # Yahoo does not give a one-element list if our query only gave one result. Therefore put the one element in a list before treating.  
    if result['query']['count'] == 1:
        raw = [result['query']['results']['quote']]
    else:
        raw = result['query']['results']['quote']
    
    # Now transform to list of dictionaries with only lower case content and without html tags. 
    for row in raw:
        stock = {}
        for key in row.keys():
            stock[str(key).lower()] = str(strip_tags(row[key]))
        stocks.append(stock)

    return stocks

'''
Get a list of tickers scraped from Yahoo Finance webpages. 
Be aware that not all stocks have their components listed on all webpages - this would give an error.
'''
def __add_tickers(webPage, tickers):

	# Uses BeautifulSoup library to parse the web page.
    componentsSoup = BeautifulSoup(webPage)

	# Finds the html table containing all tickers.
    tickerSoup = componentsSoup.find("th", text="Symbol").parent.parent
	
	# Extracts each ticker and adds it and the company name a dict in a list.
    for ticker in tickerSoup.find_all("a"):
        pair = {}
        pair['ticker'] = ticker.text
        pair['company'] = ticker.next_element.next_element.text
        tickers.append(pair)       
    
    
'''
Scrapes a list of index's components from Yahoo Finance.
Be aware that not all indices have their components listed on all webpages - this would give an error.
'''
def get_index_members(index):
	
	# Creates a yahoo finance url for the index.
	url = "http://uk.finance.yahoo.com/q/cp?s=" + index

	# For each uppercase latin letter
	tickers = []
	for i in xrange(ord('A'), ord('Z') + 1):
	
		# connects to the web page with all tickers for that letter,
		webPage = urllib.urlopen(url + "&alpha=" + chr(i))
		
		# parses the webpage and adds the tickers to their list.
		__add_tickers(webPage, tickers)
	
	return tickers