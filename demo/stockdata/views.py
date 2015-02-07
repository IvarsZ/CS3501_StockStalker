import json
import datetime
import urllib

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView

from stockstalker.models import Index, Stock
from stockdata.models import HistoricalData
import index_manager
import stock_data

# Date format constant.
DATE_FMT = "%Y-%m-%d"


'''
Redirecets the user to Yahoo Finance to download raw data file.
'''
class RedicectToYFView(RedirectView):

    def get_redirect_url(self, ticker, start, end, frequency):
        
        # Formats the dates.
        startDate = datetime.datetime.strptime(start, DATE_FMT).date()
        endDate = datetime.datetime.strptime(end, DATE_FMT).date()
        
        # Encodes the query string.
        query = urllib.urlencode({'s': ticker, 'd': endDate.month - 1, 'e' : endDate.day, 'f' : endDate.year, 'g' : frequency, 'a' : startDate.month - 1, 'b' : startDate.day, 'c' : startDate.year})

        # Returns the url.
        return 'http://ichart.finance.yahoo.com/table.csv?' + query


'''
View function for refreshing the list of index members.
'''
@login_required
def get_index_members(request, indexname):

    # converts the response to http.
    response = index_manager.update(indexname)
    return HttpResponse(response) 
    
    
'''
View function for getting current stock data in json format.
'''
@login_required
def get_current_stock_data(request, stocks):
    
    # Splits the requested stocks tickers into a list.
    splits = stocks.split(',')
    stocklist = []

    # For each ticker,
    for ticker in splits:
    
        # check that it exists.
        try:
            add = Stock.objects.get(ticker=ticker)
            stocklist.append(add)
        except Stock.DoesNotExist:
            pass;

    # Get and return the data.
    return HttpResponse(json.dumps(stock_data.get_current(stocklist)))


'''
View function for getting the tracked stocks.
'''
@login_required
def get_tracked_stocks(request):

    # Gets the tickers
    stocks = [stock.ticker for stock in request.user.investor.tracked.all()]
    return HttpResponse(json.dumps(stock_data.get_current(stocks)))


'''
A helper function extracts a dictionary of search values from a stock.
'''    
def __get_search_values(stock):
    return {'ticker':stock.ticker, 'name':stock.name, 'index':stock.index.name}
    
    
'''
Return a json list of all stocks in the database (implemented for search feature):
'''
@login_required
def list_all_stocks(request):
    
    # Gets all stocks and their search values.
    stocks = Stock.objects.all();
    return_stocks = map(__get_search_values, list(stocks))

    return HttpResponse(json.dumps(return_stocks)) 
   
def __isDangerous(data):
    
    dangerStartDate = datetime.datetime.strptime("2011-02-01", DATE_FMT).date()
    dangerEndDate = datetime.datetime.strptime("2011-02-28", DATE_FMT).date() 

    return (datetime.datetime.strptime(data['date'],DATE_FMT).date() < dangerEndDate and datetime.datetime.strptime(data['date'],DATE_FMT).date() > dangerStartDate)

def __avgvol(datum):
    sum = 0;
    count = 0;

    for data in datum:
        sum += int(data['volume'])
        count += 1
    return 0 if count == 0 else (sum/count)

def resolve_historical_intervals(stock, startdate, enddate, todaydate):
    
    intervals = []

    # Might already have some data
    have = HistoricalData.objects.filter(stock=stock).order_by('date')
    if len(have) < 1:
        return [[startdate, todaydate]]

    newest = have[len(have)-1]
    oldest = have[0]

    if startdate < oldest.date:
        intervals.append([startdate,oldest.date])

    if newest.date != todaydate:
        intervals.append([newest.date+datetime.timedelta(days=1),todaydate])

    return intervals

'''
Split the request into sections (intervals) which need to be downloaded. 

'''
def cache_historical_data(stock, startdate, enddate, todaydate, frequency):
    intervals = resolve_historical_intervals(stock, startdate, enddate, todaydate)
     
    alldata = []

    for interval in intervals:
        danger = True
        while danger:
            datum = stock_data.get_historical(stock.ticker, interval[0], interval[1], frequency) 
            avg = __avgvol(datum)

            dangerous = filter(__isDangerous, datum)
            
            if len(dangerous) < 1:
                danger = False
                break

            for d in dangerous:
                if int(d['volume']) > 5*avg:
                    d['volume'] = len(dangerous)
                else:
                    danger = False
        
        alldata.extend(datum)
    
    savelist = []
    
    # Assumes nothing in alldata is already in db.
    for point in alldata:
        newdata = HistoricalData(
            date=datetime.datetime.strptime(point['date'], '%Y-%m-%d').date(),
            stock=stock,
            price=str(float(point['closing'])),
            volume=int(point['volume']),
            cachedate=str(datetime.datetime.today().date())
        )
        savelist.append(newdata)
    HistoricalData.objects.bulk_create(savelist)

    return alldata


@login_required
def get_historical_stock_data(request, ticker, start, end, frequency):
 
    startDate = datetime.datetime.strptime(start, DATE_FMT).date()
    endDate = datetime.datetime.strptime(end, DATE_FMT).date()
    todayDate = datetime.datetime.today().date()
    
    try:
        stock = Stock.objects.get(ticker = ticker)
    except Stock.DoesNotExist:
        return json.dumps([])
    
    cache_historical_data(stock, startDate, endDate, todayDate, frequency)
    
    relevant = HistoricalData.objects.filter(stock=stock, date__gte=startDate, date__lte=endDate).values()
    relevant = list(relevant)

    for item in relevant:
        item['date'] = str(item['date'].strftime(DATE_FMT))
        item['volume'] = int(item['volume'])
        item['price'] = float(item['price'])
        item['closing'] = float(item['price'])
        item['cachedate'] = str(item['cachedate'].strftime(DATE_FMT))

    return HttpResponse(json.dumps(relevant))
