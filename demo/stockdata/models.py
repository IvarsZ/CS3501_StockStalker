from django.db import models
from stockstalker.models import Stock

'''
Model for caching historical data for graphs - has date, stock, volume and price (closing).
'''
class HistoricalData(models.Model):
    
    date = models.DateField()
    stock = models.ForeignKey(Stock)
    price = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.IntegerField()
    cachedate = models.DateField()

    def __unicode__(self):
        return self.stock.ticker
