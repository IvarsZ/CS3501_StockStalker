"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import unittest

from stockstalker.models import Index, Stock, Investor
from stockdata.models import HistoricalData

import stock_data 
import stockdata.update_indices
import stockdata.views
import datetime
import json

class StockDataTests(unittest.TestCase):
    
    ''' 
    Filter which determines which of the symbols in hpi_stocks should be added, kept and removed. 
    '''
    def testIndexFilter(self):
                
        fetched = [Stock(ticker='A', name='Company A'), Stock(ticker='B', name='Company B')]
        existing = [Stock(ticker='B', name='Company B'), Stock(ticker='C', name='Company C')]

        # Add    :  F-(FnE)
        # Keep   :  FnE
        # Remove :  E-(FnE)

        (add, keep, remove) = stockdata.update_indices.filter_index_members(fetched, existing)
        
        self.assertEqual(len(add),1)
        self.assertEqual(len(keep),1)
        self.assertEqual(len(remove),1)

        self.assertEqual(add[0].ticker, 'A')
        self.assertEqual(keep[0].ticker, 'B')
        self.assertEqual(remove[0].ticker, 'C')

    ''' 
    Test that we can remove stocks from the stocks table without screwing up the list of tracked stocks by leaving references to the deleted stocks. 
    '''
    def testStockRemove(self):
        
        # Set up an index
        index = Index(symbol='IDX', name='An Index', fetch_string='^IDX1')
        index.save()

        stock1 = Stock(index=index, ticker='A', name='Company A')
        stock2 = Stock(index=index, ticker='B', name='Company B')
        stock3 = Stock(index=index, ticker='C', name='Company C')
        stock1.save()
        stock2.save()
        stock3.save()

        investor1 = Investor(username='user1')
        investor2 = Investor(username='user2')
        investor1.save()
        investor2.save()

        investor1.tracked.add(stock1)
        investor1.tracked.add(stock2)
        investor2.tracked.add(stock2)
        investor2.tracked.add(stock3)

        # Both investors have two tracked stocks
        self.assertEquals(Stock.objects.filter(investor=investor1).count(), 2)
        self.assertEquals(Stock.objects.filter(investor=investor2).count(), 2)
 
        # Remove the stock they have in common
        stock2.delete()

        # Now they should have one each
        self.assertEquals(Stock.objects.filter(investor=investor1).count(), 1)
        self.assertEquals(Stock.objects.filter(investor=investor2).count(), 1)

        # This means that when a stock is removed for the list of stocks we know about, it will, as expected, disappear from the investor's list of tracked stocks :)

    '''
    Get symbols that are in the index. Test with FTSE100.
    '''
    def testSymbolFetcher(self):

        import ftse100TestCompanies
        #self.assertEqual(ftse100TestCompanies.companies, stock_data.get_index_members('^FTSE'))
    
    '''
    Correct data for daily pricing information should be retrieved.
    '''
    def testGetHistoricalPricingDaily(self):
    
        expected = [{'volume': '4115900', 'opening': '259.60', 'high': '261.36', 'low': '246.50', 'date': '2012-11-07', 'closing': '247.00'},
                {'volume': '3186900', 'opening': '242.30', 'high': '256.20', 'low': '242.30', 'date': '2012-11-06', 'closing': '255.80'},
                {'volume': '1224300', 'opening': '239.60', 'high': '243.70', 'low': '237.30', 'date': '2012-11-05', 'closing': '242.30'}]
        
        actual = stock_data.get_historical('EVR.L', datetime.date(2012, 11, 5), datetime.date(2012, 11, 7), 'd')
    
        self.assertEqual(expected, actual)
    
    '''
    Correct data for weekly pricing information should be retrieved.
    '''
    def testGetHistoricalPricingWeekly(self):
    
    
        expected = [{'date' : '2012-11-05', 'opening' : '2329.00', 'high' : '2360.00', 'low' : '2304.00', 'closing' : '2306.00', 'volume' : '1984800'},
                {'date' : '2012-10-29', 'opening' : '2296.00', 'high' : '2344.00', 'low' : '2290.00', 'closing' : '2342.00', 'volume' : '1892500'},
                {'date' : '2012-10-22', 'opening' : '2322.00', 'high' : '2353.00', 'low' : '2243.00', 'closing' : '2302.00', 'volume' : '3403700'}]
                
        actual = stock_data.get_historical('ULVR.L', datetime.date(2012, 10, 22), datetime.date(2012, 11, 7), 'w')
    
        self.assertEqual(expected, actual)
    
    '''
    Correct data for monthly pricing information should be retrieved.
    '''
    def testGetHistoricalPricingMonthly(self):
                
        expected = [{'volume': '6731300', 'opening': '614.50', 'high': '632.50', 'low': '608.50', 'date': '2011-11-01', 'closing': '624.50'},
                {'volume': '7512600', 'opening': '626.50', 'high': '653.50', 'low': '617.50', 'date': '2011-10-03', 'closing': '617.50'},
                {'volume': '8878600', 'opening': '619.50', 'high': '650.59', 'low': '602.00', 'date': '2011-09-02', 'closing': '638.50'}]
        
        # TODO see below        
        '''
        ALTERNATIVE SOMETIMES, BECAUSE YAHOO IS A BITCH.
        [{'high': '632.50', 'opening': '614.50', 'volume': '6731300', 'low': '608.50', 'date': '2011getCSymbolsFromYF("5EFTSE")-11-01', 'closing': '624.50'}, {'high': '653.50', 'opening': '626.50', 'volume': '7512600', 'low': '617.50', 'date': '2011-10-03', 'closing': '617.50'}, {'high': '650.59', 'opening': '619.50', 'volume': '8878600', 'low': '602.00', 'date': '2011-09-02', 'closing': '638.50'}] != [{'volume': '6723000', 'opening': '614.50', 'high': '632.50', 'low': '608.50', 'date': '2011-11-01', 'closing': '624.50'}, {'volume': '7502400', 'opening': '626.50', 'high': '653.50', 'low': '617.50', 'date': '2011-10-03', 'closing': '617.50'}, {'volume': '8865900', 'opening': '619.50', 'high': '650.59', 'low': '602.00', 'date': '2011-09-02', 'closing': '638.50'}]
        '''
                
        actual = stock_data.get_historical('NG.L', datetime.date(2011, 9, 2), datetime.date(2011, 11, 14), 'm')
    
        #self.assertEqual(expected, actual)
    
    '''
    Correct data should be retrieved if an index symbol is used instead of a symbol of a stock company.
    '''
    def testGetHistoricalPricingIndex(self):
    
        expected =  [{'volume': '000', 'opening': '6672.70', 'high': '6838.60', 'low': '6672.70', 'date': '2000-09-01', 'closing': '6795.00'},
                 {'volume': '000', 'opening': '6615.10', 'high': '6675.70', 'low': '6585.20', 'date': '2000-08-31', 'closing': '6672.70'},
                 {'volume': '000', 'opening': '6586.30', 'high': '6624.90', 'low': '6586.10', 'date': '2000-08-30', 'closing': '6615.10'},
                 {'volume': '000', 'opening': '6563.70', 'high': '6601.10', 'low': '6560.20', 'date': '2000-08-29', 'closing': '6586.30'}]

        actual = stock_data.get_historical('^FTSE', datetime.date(2000, 8, 29), datetime.date(2000, 9, 2), 'd')
    
        #self.assertEqual(expected, actual)
    
    '''
    DataNotFoundException should be thrown when a non exising symbol "agegasf" is used.
    ''' 
    def testGetHistoricalPricingInvalidSymbol(self):
    
        self.assertRaises(stock_data.DataNotFoundException, stock_data.get_historical,'agegasf', datetime.date(2012, 11, 5), datetime.date(2012, 11, 7), 'd')
    
    '''
    InvalidDatesException should be thrown when the end date is before the start date.
    '''
    def testGetHistoricalPricingEndBeforeStartDate(self):
    
        self.assertRaises(stock_data.InvalidDatesException, stock_data.get_historical,'ULVR.L', datetime.date(2011, 11, 5), datetime.date(2011, 11, 4), 'd')
        
    '''
    InvalidDatesException should be thrown when the end date is after the current date.
    '''
    def testGetHistoricalPricingEndAfterCurrentDate(self):
    
        self.assertRaises(stock_data.InvalidDatesException, stock_data.get_historical,'ULVR.L', datetime.date(2011, 11, 5), datetime.date(3000, 11, 4), 'd')
        
    '''
    InvalidFrequencyException should be thrown when the frequency is not 'd', 'w' nor 'm' throws .
    '''
    def testGetHistoricalPricingInvalidFrequency(self):
    
        self.assertRaises(stock_data.InvalidFrequencyException, stock_data.get_historical,'ULVR.L', datetime.date(2011, 11, 4), datetime.date(2011, 11, 5), 'g')

    def testCaching(self):

        # Add index
        index = Index(symbol="FTSE100", name="FTSE100", fetch_string="FTSE", currency="GBP")
        index.save()

        # Add stock
        stock = Stock(index=index, ticker="NXT.L", name="STOCK")
        stock.save()

        self.assertFalse(HistoricalData.objects.all().exists())

        startdate = datetime.datetime.strptime("2012-11-01", "%Y-%m-%d").date()
        enddate = datetime.datetime.strptime("2012-11-20", "%Y-%m-%d").date()
        todaydate = datetime.datetime.today().date()
        frequency = 'd'

        # Get some data
        data = stockdata.views.cache_historical_data(stock, startdate, enddate, todaydate, frequency)
        
        import time
        time.sleep(3)

        length1 = len(HistoricalData.objects.all())
        self.assertNotEquals(length1, 0)
 
        nomoredata = stockdata.views.cache_historical_data(stock, startdate, enddate, todaydate, frequency)
        length2 = len(HistoricalData.objects.all()) 

        self.assertNotEquals(length2, 0)

        # Add range that starts before previous range
        startdate2 = datetime.datetime.strptime("2012-10-01", "%Y-%m-%d").date() 
        moredata = stockdata.views.cache_historical_data(stock, startdate2, enddate, todaydate, frequency) 
        length3 = len(moredata)

        self.assertNotEquals(len(HistoricalData.objects.all()),length1) # Should have grown
        self.assertEquals(len(HistoricalData.objects.all()), length1+length3)

