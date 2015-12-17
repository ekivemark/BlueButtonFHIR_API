# -*- coding: utf-8 -*-
"""
bbofuser: apps.v1api.views
FILE: ogets
Created: 9/27/15 7:04 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from oauth2_provider.decorators import protected_resource
from oauth2_provider.models import AbstractApplication, AccessToken
from oauth2_provider.views.generic import ProtectedResourceView

from django.conf import settings
from django.http import HttpResponse

from apps.v1api.views.patient import get_patient

class Hello(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, OAuth2!')

@protected_resource()
def Patient(request, *args, **kwargs):
    # TODO: get this working

    if settings.DEBUG:
        print("in apps.v1api.views.ogets.Patient")
        print("request:", request)

    result = get_patient(request, *args, **kwargs)
    if settings.DEBUG:
        print("Results:", result)

    return result
