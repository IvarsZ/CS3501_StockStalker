from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from djcelery.models import CrontabSchedule, IntervalSchedule, TaskState, WorkerState, PeriodicTask

from stockstalker.models import Investor, Index
import stockdata.stock_data

'''
Class for Modifying the admin view of indices.
'''
class IndexAdmin(admin.ModelAdmin):
    
    # Fields of the indices to display.
    list_display = ('symbol', 'name', 'fetch_string', 'reload_link')

    def save_model(self, request, obj, form, change):
        obj.save()
        
        # Reloads the list of stocks.
        stockdata.views.get_index_members(request, obj.symbol)
    
    '''
    Gives a link to automatically update the list of stocks of an index.
    ''' 
    def reload_link(self, obj):
           return "<a href='%s'>Reload</a>" % reverse('get_index_members', args=(obj.symbol,))
           
    reload_link.allow_tags = True

# Registers the new index admin view and uses user administration view for investors.
admin.site.register(Index, IndexAdmin)
admin.site.register(Investor, UserAdmin)

# Unregisters (removes) all unnecessary admin views, that are automatically registered by django.
admin.site.unregister(User)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(PeriodicTask)
