#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: apps.v1api.views.crosswalk
Created: 12/28/15 10:30 AM

Crosswalk utilities

"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.conf import settings
from django.contrib import messages

from ..models import Crosswalk
from ..utils import concat_string


def lookup_xwalk(request, element='fhir_url_id'):
    # Lookup up in Crosswalk with request.user
    # First we need to check for AnonymousUser

    if request.user.id ==None:
        if settings.DEBUG:
            print('Sorry - AnonymousUser gets no information')
        return None
    elif settings.DEBUG:
        print("lookup_xwalk:Request User Beneficiary(Patient):",
              request.user)
    else:
        pass

    try:
        xwalk = Crosswalk.objects.get(user=request.user)
    except Crosswalk.DoesNotExist:
        messages.error(request, "Unable to find Patient ID")
        return None

    if element.lower() == 'fhir_url_id' and xwalk.fhir_url_id == "":

        err_msg = ['Sorry, We were unable to find',
                   'your record', ]
        exit_message = concat_string("",
                                     msg=err_msg,
                                     delimiter=" ",
                                     last=".")
        messages.error(request, exit_message)
        return None

    else:
        if settings.DEBUG:
            print("We got a match on ",
                  request.user,
                  ":",
                  xwalk.fhir_url_id)
        return xwalk.fhir_url_id

