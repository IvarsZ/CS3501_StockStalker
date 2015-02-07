'''
Tests for the stockstalker application.
'''

from django.test import TestCase

from django.test.client import RequestFactory

from stockstalker.models import Index, Stock, Investor
from stockstalker.views import InvestorView
from stock_evaluator import StockMetrics
import views, stock_evaluator, tasks

class ModelTests(TestCase):
    
    def setUp(self):

        self.index1 = Index(symbol='IXD', name='An index', fetch_string='^ftse')
        self.index1.save()

        self.index2 = Index(symbol='IXD2', name='An index', fetch_string='^ftai')
        self.index2.save()  

        self.stock1 = Stock(index=self.index1, ticker='AAL.L', name="Some company")
        self.stock1.save()
        
        self.stock2 = Stock(index=self.index2, ticker='ACC.L', name="Some company")
        self.stock2.save()
        
        self.factory = RequestFactory()


    '''
    Verify that stock and index have 1:x relationships.
    '''
    def test_stock_index_relationships(self):

        self.assertEquals(Index.objects.all().count(), 2)
        self.assertEquals(Stock.objects.all().count(), 2)
        self.assertEquals(Stock.objects.get(index=self.index1), self.stock1)
        self.assertEquals(Stock.objects.get(index=self.index2), self.stock2)
 

    '''
    Verify that investor and stocks have many to many relationship.
    '''
    def test_investor_relationships(self):
        
        self.investor1 = Investor(username='user1')
        self.investor1.save()

        self.investor2 = Investor(username='user2')
        self.investor2.save()

        self.investor1.tracked.add(self.stock1)
        self.investor1.save()

        self.assertEquals(Investor.objects.get(tracked=self.stock1), self.investor1)
        self.assertEquals(Stock.objects.get(investor=self.investor1), self.stock1)
    
    
    '''
    Tests for adding/removing stocks to the tracked stocks
    '''
    
    
    def test_add_stock(self):
        
        self.investor1 = Investor(username='user1')
        self.investor1.save()
        
        self.assertEquals(self.investor1.tracked.count(), 0)
        views.add_stock(self.investor1, self.stock1.ticker)
        
        self.assertEquals(self.investor1.tracked.count(), 1)
        self.assertEquals(self.investor1.tracked.get(ticker=self.stock1.ticker), self.stock1)
        
    def test_add_existing_stock(self):
    
        self.investor1 = Investor(username='user1')
        self.investor1.save()
        
        self.investor1.tracked.add(self.stock1)
        self.investor1.save()
        
        self.assertEquals(self.investor1.tracked.count(), 1)
        views.add_stock(self.investor1, self.stock1.ticker)
        
        self.assertEquals(self.investor1.tracked.count(), 1)
        self.assertEquals(self.investor1.tracked.get(ticker=self.stock1.ticker), self.stock1)
        
    def test_add_multiple_stocks(self):
    
        self.investor1 = Investor(username='user1')
        self.investor1.save()
        
        self.assertEquals(self.investor1.tracked.count(), 0)
        views.add_stock(self.investor1, self.stock1.ticker)
        views.add_stock(self.investor1, self.stock2.ticker)
        
        self.assertEquals(self.investor1.tracked.count(), 2)
        self.assertEquals(self.investor1.tracked.get(ticker=self.stock1.ticker), self.stock1)
        self.assertEquals(self.investor1.tracked.get(ticker=self.stock2.ticker), self.stock2)
        
    def test_add_stock_multiple_users(self):
    
        self.investor1 = Investor(username='user1')
        self.investor1.save()
        
        self.investor2 = Investor(username='user2')
        self.investor2.save()
        
        views.add_stock(self.investor1, self.stock1.ticker)
        self.assertEquals(self.investor2.tracked.count(), 0)
        
    def test_remove_stock(self):
    
        self.investor1 = Investor(username='user1')
        self.investor1.save()
        
        self.investor1.tracked.add(self.stock1)
        self.investor1.save()
        
        self.assertEquals(self.investor1.tracked.count(), 1)
        views.remove_stock(self.investor1, self.stock1.ticker)
        
        self.assertEquals(self.investor1.tracked.count(), 0)
        
    def test_remove_nonexisting_stock(self):
    
        self.investor1 = Investor(username='user1')
        self.investor1.save()
        
        self.assertEquals(self.investor1.tracked.count(), 0)
        views.remove_stock(self.investor1, self.stock1.ticker)
        
        self.assertEquals(self.investor1.tracked.count(), 0)
        
    def test_remove_multiple_stocks(self):
    
        self.investor1 = Investor(username='user1')
        self.investor1.save()
        
        self.investor1.tracked.add(self.stock1)
        self.investor1.tracked.add(self.stock2)
        self.investor1.save()
        
        self.assertEquals(self.investor1.tracked.count(), 2)
        views.remove_stock(self.investor1, self.stock1.ticker)
        views.remove_stock(self.investor1, self.stock2.ticker)
        
        self.assertEquals(self.investor1.tracked.count(), 0)
        
    def test_add_remove_stock(self):
    
        self.investor1 = Investor(username='user1')
        self.investor1.save()
        
        self.assertEquals(self.investor1.tracked.count(), 0)
        views.add_stock(self.investor1, self.stock1.ticker)
        views.remove_stock(self.investor1, self.stock1.ticker)
        self.assertEquals(self.investor1.tracked.count(), 0)
        
    def test_remove_stock_multiple_users(self):
    
        self.investor1 = Investor(username='user1')
        self.investor1.save()
        
        self.investor2 = Investor(username='user2')
        self.investor2.save()
        
        self.investor1.tracked.add(self.stock1)
        self.investor1.save()
        
        self.investor2.tracked.add(self.stock1)
        self.investor1.save()
        
        views.remove_stock(self.investor1, self.stock1.ticker)
        self.assertEquals(self.investor2.tracked.count(), 1)
    
    '''
    Tests for stock evaluation.
    '''

    
    def test_get_stock_scores(self):
        
        # Normal numbers.
        metrics = StockMetrics(10, 15, 12.5, 2.5, 3.3, 2.1, 5.4, 3.4, 0.2)
        self.assertEquals(stock_evaluator.evaluate_stock(metrics), 12.125)
        
    def test_get_stock_scores2(self):
    
        # 0 price, low score.
        metrics = StockMetrics(0, 15, 12.5, 2.5, 3.3, 2.1, 5.4, 3.4, 0.2)
        self.assertEquals(stock_evaluator.evaluate_stock(metrics), stock_evaluator.LOW_SCORE)
        
    def test_get_stock_scores3(self):
        
        # over price book limit.
        metrics = StockMetrics(10, 15, 12.5, 2.5, stock_evaluator.PRICE_BOOK_LIMIT + 1, 2.1, 5.4, 3.4, 0.2)
        self.assertEquals(stock_evaluator.evaluate_stock(metrics), 12.125)
        
    def test_get_stock_scores4(self):
        
        # below price book limit.
        metrics = StockMetrics(10, 15, 12.5, 2.5, stock_evaluator.PRICE_BOOK_LIMIT - 1, 2.1, 5.4, 3.4, 0.2)
        self.assertEquals(stock_evaluator.evaluate_stock(metrics), 17.125)
        
    def test_get_stock_scores5(self):
        
        # price-sales is 0.
        metrics = StockMetrics(10, 15, 12.5, 2.5, 3, 0, 5, 3, 0.2)
        self.assertEquals(stock_evaluator.evaluate_stock(metrics), 6.625)
        
    def test_get_stock_scores6(self):
        
        # price-earnings to growth ratio is 0, almost low score.
        metrics = StockMetrics(10, 15, 12.5, 2.5, 3.3, 2.1, 5.4, 0, 0.2)
        self.assertEquals(stock_evaluator.evaluate_stock(metrics), 7.125)
        
    def test_get_stock_scores7(self):
        
        # price-earnings ratio is 0, low score.
        metrics = StockMetrics(10, 15, 12.5, 0, 3.3, 2.1, 5.4, 3, 0.2)
        self.assertEquals(stock_evaluator.evaluate_stock(metrics), -10000.375)
        
    def test_get_stock_scores8(self):
        
        # EPS prediction is 0.
        metrics = StockMetrics(10, 15, 12.5, 2.5, 3.3, 2.1, 5.4, 3.4, 0)
        self.assertEquals(stock_evaluator.evaluate_stock(metrics), 12.125)
        
    def test_get_stock_scores9(self):
        
        # high EPS prediction.
        metrics = StockMetrics(10, 15, 12.5, 2.5, 3.3, 2.1, 5.4, 3.4, 100)
        self.assertEquals(stock_evaluator.evaluate_stock(metrics), 13.125)
        
    '''
    Tests updating stock recommendations.
    '''
    def test_update_stock_recommendations(self):
    
        # Initially stocks have no scores.
        for stock in Stock.objects.all():
            self.assertEquals(stock.score, None)
            
        tasks.update_recommendations()
        
        # Have scores after update.
        for stock in Stock.objects.all():
            self.assertTrue(stock.score != None)