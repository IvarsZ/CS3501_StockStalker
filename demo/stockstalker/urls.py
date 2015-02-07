from django.conf.urls import patterns, url
from views import ProfileView, StockView, InvestorUpdate
from django.contrib.auth.views import password_change, password_change_done

urlpatterns = patterns('stockstalker.views',

    # Url to the profile.
    url(r'^/$', ProfileView.as_view()),
    
    # Url to individual stock.
    url(r'^/stock/(?P<pk>[\w|\.]+)', StockView.as_view()),
    
    # Url after successfully changing the password.
    url(r'^/account/password_change/done$', password_change_done),
    
    # Url to change the password.
    url(r'^/account/password_change/$', password_change, name = 'password_change'),
    
    # Url for investor to update his account details.
    url(r'^/account/$', InvestorUpdate.as_view()),
    
    # Url for adding a stock to investors profile.
    url(r'^/add/(?P<ticker>[\w|\.]+)', 'try_add_stock'),
    
    # Url for removing a stock from investors profile.
    url(r'^/remove/(?P<ticker>[\w|\.]+)', 'try_remove_stock'),
)

