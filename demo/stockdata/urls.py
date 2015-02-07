from django.conf.urls import patterns, url
from stockdata.views import RedicectToYFView

urlpatterns = patterns('stockdata.views',

    # Redirect to raw historical data.
    url(r'^/historical/raw/(?P<ticker>[\w|\.]+)/(?P<start>\d{4}-\d{2}-\d{2})/(?P<end>\d{4}-\d{2}-\d{2})/(?P<frequency>[wdm])/$', RedicectToYFView.as_view()),
    
    # Gets historical stock data.
    url(r'^/historical/(?P<ticker>[\w|\.]+)/(?P<start>\d{4}-\d{2}-\d{2})/(?P<end>\d{4}-\d{2}-\d{2})/(?P<frequency>[wdm])/$', 'get_historical_stock_data'),
	
    # Gets list of index members.
    url(r'^/index/members/(?P<indexname>[\w|\.]+)/$', 'get_index_members', name='get_index_members'),
    
    # Gets current state of stock.
    url(r'^/current/(?P<stocks>[\w|\.|,]+)/$', 'get_current_stock_data'),

    # Gets urls tracked by logged-in investor.
    url(r'^/tracked/', 'get_tracked_stocks'),
    
    # Returns all stocks for search.
    url(r'^/allstocks/', 'list_all_stocks'),
)
