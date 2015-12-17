"""
bbofuser: apps.v1api
FILE: urls.py
Created: 8/6/15 6:34 PM

We will call this from the apps.api namespace as v1

i.e. [Server_root]/api/v1/

"""
__author__ = 'Mark Scrimshire:@ekivemark'

# TODO: Implement REST API with pass through to FHIR Server

from django.conf.urls import (patterns,
                              include,
                              url)
from django.contrib import admin

# from apps.subacc.views import subaccount_authenticate

from apps.v1api.views.home import *
from apps.v1api.views.patient import (get_patient,
                                      get_eob,
                                      get_eob_view)
from apps.v1api.views.ogets import (Hello,
                                    Patient)

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples: These are used by sub-accounts
                       # or master accounts
                       url(r'^$', 'apps.v1api.views.home.api_index',
                           name='home'),
                       url(r'^patient$',
                           'apps.v1api.views.patient.get_patient',
                           name='patient'),
                       url(r'^eob/',
                           'apps.v1api.views.patient.get_eob',
                           name='eob'),
                       url(r'^eobview/(?P<eob_id>[-\w]+)$',
                           'apps.v1api.views.patient.get_eob_view',
                           name='eobview'),
                       # OAuth entry points are here
                       # These will only be used by OAuth authorized apps
                       # These are the resource servers
                       url(r'^o/hello', Hello.as_view()),
                       # Add more oauth endpoints here
                       url(r'^o/patient', 'apps.v1api.views.ogets.Patient'),

                       url(r'^admin/', include(admin.site.urls)),

                       )