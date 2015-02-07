from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

import stock_evaluator

# Constants for standart lengths of character fields.
SHORT_STR_LEN = 31
LONG_STR_LEN = 127

'''
Django model for indices.
'''
class Index(models.Model):
    
    symbol = models.CharField(max_length=SHORT_STR_LEN);            # Symbol (string) used to identify the index the system.
    name = models.CharField(max_length=LONG_STR_LEN);               # Name of the index.
    fetch_string = models.CharField(max_length=SHORT_STR_LEN);      # String identifying the index in the data repository (Yahoo Finance).
    currency = models.CharField(max_length=SHORT_STR_LEN);          # Trading curreny in the index.

    def __unicode__(self):
        return self.symbol

'''
Django model for stocks.
'''
class Stock(models.Model):
    
    index = models.ForeignKey(Index)                                            # The index to which this stock belongs.
    ticker = models.CharField(max_length=SHORT_STR_LEN, primary_key=True)       # The ticker used to identify this stock in the system
                                                                                # and data repository.
    
    name = models.CharField(max_length=LONG_STR_LEN)                            # Name of the stock.
    score = models.DecimalField(max_digits=8, decimal_places=2, null=True)      # Score representing systems evaluation of the stock.

    def __unicode__(self):
        return self.ticker

'''
Django model for investors, extends user for authorization and authentication.
'''
class Investor(User):
    
    tracked = models.ManyToManyField(Stock)     # The stocks tracked by the investor.

    def __unicode__(self):
        return self.username
