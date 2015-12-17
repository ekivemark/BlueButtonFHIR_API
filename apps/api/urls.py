"""
bbofuser: api
FILE: urls
Created: 8/4/15 10:15 PM

Access to the FHIR API

"""
__author__ = 'Mark Scrimshire:@ekivemark'

# DONE: Implement REST API v1 (apps.v1api) napespace v1
# DONE: Build Authentication using Device Account

from django.conf.urls import (patterns,
                              include,
                              url)
from django.contrib import admin

from apps.api.views import *

# from apps.subacc.views import subaccount_authenticate

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$',
                           'apps.api.views.api_index',
                           name='home'),
                       # url(r'^login$',
                       #     'apps.subacc.views.subaccount_authenticate',
                       #     name='login'),
                       # v1 api entry point
                       # Oauth entry point is found inside v1api
                       # apps.v1api.urls
                       url(r'^v1/',
                           include('apps.v1api.urls',
                                   namespace='v1')),

                       url(r'^admin/', include(admin.site.urls)),

                       )
