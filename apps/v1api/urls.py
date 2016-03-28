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
                                      get_eob_view,)

from apps.v1api.views.ogets import (Hello,
                                    o_patient,
                                    Patients,
                                    o_explanationofbenefit,
                                    open_patient,
                                    open_explanationofbenefit)

from apps.v1api.views.apidocs import (ResourceTypeList,
                                      ResourceControlList)

from apps.v1api.views.eob import (ExplanationOfBenefit,
                                  PatientExplanationOfBenefit)

admin.autodiscover()

urlpatterns = [
                       # Examples: These are used by sub-accounts
                       # or master accounts
                       url(r'^$', api_index,
                           name='home'),

                       #url(r'^Patient$/(?P<patient_id>[-\w]+)$',
                       url(r'^Patient/(?P<patient_id>\w+|)$',
                           get_patient,
                           name='patient_by_id'),
                       url(r'^Patient$',
                           get_patient,
                           name='patient'),

                       url(r'^eob/',
                           get_eob,
                           name='eob'),
                       url(r'^ExplanationOfBenefit$',
                           ExplanationOfBenefit,
                           name='ExplanationOfBenefit'),
                       url(r'^eobview/(?P<eob_id>[-\w]+)$',
                           get_eob_view,
                           name='eobview'),

                       url(r'^PatientExplanationOfBenefit/(?P<patient_id>[-\w]+)$',
                           PatientExplanationOfBenefit,
                           name='PatientExplanationOfBenefit_by_id'),

                       url(r'^PatientExplanationOfBenefit$',
                           PatientExplanationOfBenefit,
                           name='PatientExplanationOfBenefit'),

                       # OAuth entry points are here
                       # These will only be used by OAuth authorized apps
                       # These are the resource servers
                       url(r'^o/hello', Hello.as_view()),

                       url(r'^open/Patient/(?P<patient_id>\w+|)$', open_patient, name='open_patient'),

                       # Add more oauth endpoints here
                       #url(r'^o/Patient/(?P<patient_id>\w+|)$', Patients.as_view(), name='fhir_patient'),
                       url(r'^o/Patient/(?P<patient_id>\w+|)$', o_patient, name='fhir_patient'),
                       url(r'^o/Patient', o_patient),

                       url(r'^o/ExplanationOfBenefit$', o_explanationofbenefit),

                       url(r'^open/ExplanationOfBenefit$', open_explanationofbenefit),

                       # Resources
                       url(r'^resourcetype',ResourceTypeList.as_view(),
                           name = "resourcetype"),

                       url(r'^resourcecontrol',ResourceControlList.as_view(),
                           name="resourcecontrol"),
                       # Admin
                       url(r'^admin/', include(admin.site.urls)),

                       ]