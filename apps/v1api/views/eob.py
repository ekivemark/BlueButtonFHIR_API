#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: apps.v1api.views.eob
Created: 12/28/15 9:33 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

import requests

from xml.dom import minidom

from oauth2_provider.decorators import protected_resource
from oauth2_provider.models import AbstractApplication, AccessToken
from oauth2_provider.views.generic import ProtectedResourceView, View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import ListView

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpRequest)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from apps.v1api.views.patient import get_patient
from apps.v1api.views.crosswalk import lookup_xwalk
from apps.v1api.utils import (build_params)


class EOB(ListView):
    if settings.DEBUG:
        print("in apps.v1api.views.eob")

    def get(self, request, eob_id, *args, **kwargs):
        # This is an ExplanationOfBenefit profile GET
        #
        # use request.user to lookup a crosswalk
        # get the FHIR Patient ID
        # Call the FHIR Patient Profile
        # Return the result
        # EOB will need to look up request.user and apply a filter on the EOB
        # The filter in search Parameters will be the GUID
        # We need to load the GUID when we are loading EOBs and
        # Patient Records.

        if settings.DEBUG:
            print("in EOB.get with", eob_id)

        xwalk_id = lookup_xwalk(request, )
        if settings.DEBUG:
            print("crosswalk:", xwalk_id)

        if xwalk_id == None:
            return HttpResponseRedirect(reverse_lazy('api:v1:home'))

        if settings.DEBUG:
            print("now we need to evaluate the parameters and arguments"
                  " to work with ", xwalk_id, "and ", request.user)
            print("GET Parameters:", request.GET, ":")

        if patient_id == xwalk_id:
            key = eob_id
        else:
            key = xwalk_id.strip()

        in_fmt = "json"
        Txn = {'name': "ExplanationOfBenefit",
           'display': 'ExplanationOfBenefit',
           'mask': True,
           'server': settings.FHIR_SERVER,
           'locn': "/baseDstu2/ExplanationOfBenefit/",
           'template': 'v1api/eob.html',
           'in_fmt': in_fmt,
           }

        skip_parm = ['_id']
        pass_params = build_params(request.GET, skip_parm)

        pass_to = Txn['server'] + Txn['locn'] + key + "/"

        print("Here is the URL to send, %s now get parameters" % pass_to)

        if pass_params != "":
            pass_to = pass_to + pass_params

        try:
            r = requests.get(pass_to)

        except requests.ConnectionError:
            if settings.DEBUG:
                print("Problem connecting to FHIR Server")
            messages.error(request, "FHIR Server is unreachable." )
            return HttpResponseRedirect(reverse_lazy('api:v1:home'))

        text_out = ""
        if '_format=xml' in pass_to:
            text_out= minidom.parseString(r.text).toprettyxml()
        else:
            text_out = r.json()

        return HttpResponse('This is the EOB Pass Thru %s using %s '
                            'and with response of %s' % (xwalk_id,
                                                         pass_to,
                                                         text_out))


@csrf_exempt
@login_required
@protected_resource(scopes=['read write_consent'])
def ExplanationOfBenefit(request, *args, **kwargs):
    """
    Function-based interface to ExplanationOfBenefit
    :param request:
    :return:
    """

    if settings.DEBUG:
        print("In apps.v1api.views.eob.ExplanationOfBenefit Function")

        print("request:", request.GET)

    process_mode = request.META['REQUEST_METHOD']

    send_back = 'Hello, %s' % request.user
    send_back += ':ExplanationOfBenefit [mode=%s]' % process_mode
    if args:
        send_back += '[args=%s]' % (args)
    if kwargs:
        send_back += '[kwargs=%s]' % (kwargs)

    return HttpResponse(send_back)

