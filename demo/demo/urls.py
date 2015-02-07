from django.conf.urls import patterns, include, url

# Enables the admin:
from django.contrib import admin
from django.views.generic.base import RedirectView
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^stockstalker', include('stockstalker.urls')),

    url(r'^stockdata', include('stockdata.urls')),

    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'stockstalker.views.try_logout'),
    url(r'^$', RedirectView.as_view(url='/stockstalker')),
)
