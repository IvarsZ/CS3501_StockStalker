import datetime

from celery import Celery
from celery.task import periodic_task
from celery.task import task
from celery.task.schedules import crontab

from stockdata.models import HistoricalData

import index_manager

celery = Celery('stockdata_tasks')
          
'''
Updates stocks for all indices every 24 hours.
'''
@periodic_task(run_every=crontab(hour="*/24"))
def update_indeces():
    for index in Index.objects.all():
        index_manager.reload_index_members(index.symbol)

'''
Clears the cache every 24 hours.
'''
@periodic_task(run_every=crontab(hour="*/24"))        
def clear_cache():
    
    # Calculates the expiry date, filters and deletes everything before it.
    expire = datetime.datetime.today().date() - datetime.timedelta(days=7)
    HistoricalData.objects.filter(cachedate__lte=expire).delete()