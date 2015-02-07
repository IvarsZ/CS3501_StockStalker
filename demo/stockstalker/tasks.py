from celery import Celery
from celery.task import periodic_task
from celery.task.schedules import crontab

from stockstalker.models import Stock, Index
from stockstalker import stock_evaluator

celery = Celery('stockstalker_tasks')

CHUNK_SIZE = 20

'''
Updates the recommendations of all stocks every hour.
'''
@periodic_task(run_every=crontab(minute="*/60"))
def update_recommendations():

    # Gets all stocks and splits them in chunks.
    stocks = Stock.objects.all()
    chunks = [stocks[i : i + CHUNK_SIZE] for i in range(0, len(stocks), CHUNK_SIZE)]

    # For each chunk,
    for chunk in chunks:
    
        # gets the scores,
        scores = stock_evaluator.get_stock_scores(chunk)
        
        # and saves them.
        for i in xrange(0, len(chunk)):
            chunk[i].score = scores[i]
            print scores[i]
            print chunk[i].score
            chunk[i].save()