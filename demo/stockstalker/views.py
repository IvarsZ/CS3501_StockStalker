from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse
from django.forms import ModelForm

from models import Investor, Stock

import json

'''
Base mixin for anything that requires the investor to be authenticated.
'''
class InvestorMixin(SingleObjectMixin):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):

        #Ensures that only authenticated users can access the view.
        return super(InvestorMixin, self).dispatch(request, *args, **kwargs)

'''
View class for investor, gets the user properly and his context details.
'''        
class InvestorView(InvestorMixin):
    
    model = Investor
    
    def get_context_data(self, **kwargs):
 
        # Attaches the top recommended stocks to the context for the template.
        context = super(InvestorView, self).get_context_data(**kwargs)
        context['recommended'] = Stock.objects.order_by('-score')[:5]

        return context

    def get_object(self):
    
        # Identifies the investor by the user field from the user super class.
        return Investor.objects.get(user_ptr=self.request.user)

'''
View for the user profile.
'''
class ProfileView(InvestorView, DetailView):
    
    template_name = 'profile.html'
    
'''
Form for updating the details of the investor.
'''
class InvestorForm(ModelForm):

    class Meta:
        model = Investor
        
        # only includes first name, last name and email in the form.
        fields = ('first_name', 'last_name', 'email')

'''
View for updating the details of the investor.
'''
class InvestorUpdate(InvestorView, UpdateView):
    
    template_name = 'account.html'
    form_class = InvestorForm
    
    def get_success_url(self):
        return '/stockstalker/account'

'''
View for individual stocks.
'''
class StockView(InvestorMixin, DetailView):

    model = Stock
    template_name = 'stock.html'

    def get_context_data(self, **kwargs):
        
        # Attacjes the investor to the context, to have his tracked stocks in the template (for add/remove).
        context = super(StockView, self).get_context_data(**kwargs)
        context['investor'] = Investor.objects.get(user_ptr=self.request.user) 
        
        return context

'''
Logout, redirects to the home page.
'''
def try_logout(request):
    logout(request)
    return redirect('/')

'''
Adds a stock identified by a ticker to the investor's tracked stocks.
'''
def add_stock(investor, ticker):
    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist:
        return (False, 'Stock ' + stock.ticker + ' does not exist')

    if investor.tracked.filter(ticker=stock.ticker).exists():
        return (True, 'Stock ' + stock.ticker + ' already tracked')

    try:
        investor.tracked.add(stock)
    except Exception:
        return (False, 'An unknown error ocurred')

    return (True,'Stock '+ stock.ticker + ' was added to the watchlist')

'''
Removes a stock identified by a ticker from the investor's tracked stocks.
'''
def remove_stock(investor, ticker):
    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist:
        return (False, 'Stock '+ stock.ticker + ' does not exist') 
    
    if not investor.tracked.filter(ticker=stock.ticker):
        return (True, 'Stock was ' + stock.ticker + ' not tracked.')

    try: 
        investor.tracked.remove(stock)
    except Exception:
        return (False, 'An unknown error ocurred')

    return (True, 'Stock ' + stock.ticker + ' was removed from the watchlist.')

'''
Helper function to return a json response of the success/failure of the adding/removal.
'''
def __encodeResult((result, message)):
    send = {'result':result,'message':message}
    return json.dumps(send)

'''
View function for attempting to add a stock to investor's tracked stocks.
'''
@login_required
def try_add_stock(request, ticker):
    return HttpResponse(__encodeResult(add_stock(request.user.investor, ticker)))

'''
View function for attempting to remove a stock from investor's tracked stocks.
'''
@login_required
def try_remove_stock(request, ticker):
    return HttpResponse(__encodeResult(remove_stock(request.user.investor, ticker)))
