#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: apps.v1api.views.eob
Created: 12/28/15 9:33 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

import json
import requests

from collections import OrderedDict

from xml.dom import minidom
from xml.etree import ElementTree as ET

from oauth2_provider.decorators import protected_resource
from oauth2_provider.models import AbstractApplication, AccessToken
from oauth2_provider.views.generic import ProtectedResourceView, View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import ListView

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import (reverse_lazy,
                                      reverse)
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpRequest,
                         JsonResponse)

from fhir.utils import kickout_404

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from apps.v1api.views.patient import get_patient
from apps.v1api.views.crosswalk import lookup_xwalk
from apps.v1api.views.patient import (cms_not_connected,
                                      process_page,
                                      publish_page)
from apps.v1api.utils import (build_params,
                              get_format,
                              concat_string)

from ..models import Crosswalk

from bbapi.utils import FhirServerUrl


#@csrf_exempt
@login_required
#@protected_resource(scopes=['read write_consent'])
def ExplanationOfBenefit(request, eob_id=None, Access_Mode=None, *args, **kwargs):
    """
    Function-based interface to ExplanationOfBenefit
    :param request:
    :return:

    Use Cases:
    1. No eob_id: Do Search and apply patient=Patient/User.Crosswalk.fhir_url_id
    2. eob_id: Do Search and get eob with patient filter

    http://bluebuttonhapi-test.hhsdevcloud.us/baseDstu2/ExplanationOfBenefit
        ?_id=1286291&patient=Patient/1286160

    3. eob_id and Access_mode = OPEN



    """

    if settings.DEBUG:
        print("In apps.v1api.views.eob.ExplanationOfBenefit Function")

        print("request:", request.GET)

    process_mode = request.META['REQUEST_METHOD']

    patient_id = lookup_xwalk(request)
    # try:
    #     xwalk = Crosswalk.objects.get(user=request.user)
    # except Crosswalk.DoesNotExist:
    #     messages.error(request, "Unable to find Patient ID")
    #     return HttpResponseRedirect(reverse('api:v1:home'))
    #
    if patient_id == None:
        return HttpResponseRedirect(reverse('api:v1:home'))

    in_fmt = "json"
    get_fmt = get_format(request.GET)

    if settings.DEBUG:
        print("Request.GET :", request.GET)
        print("KWargs      :", kwargs)
        print("FHIR URL ID :", patient_id)

    # We should have the xwalk.FHIR_url_id
    # So we will construct the EOB Identifier to include

    # We will deal internally in JSON Format if caller does not choose
    # a format
    in_fmt = "json"
    get_fmt = get_format(request.GET)

    pass_to = FhirServerUrl()
    pass_to += "/ExplanationOfBenefit/"

    key = patient_id.strip()
    patient_filter= "patient=Patient/" + key

    # pass_to += patient_filter

    skip_parm = ['_id', '_format']

    got_parms = build_params(request.GET, skip_parm)[1:]

    if got_parms:
        print("Got parms:", got_parms)
        pass_to += "?" + got_parms

    if Access_Mode == "OPEN":
        pass
    else:
        if "?" in pass_to:
            pass_to += "&" + patient_filter
        else:
            pass_to += "?" + patient_filter

    if eob_id:
        if "?" in pass_to:
            pass_to += "&"
        else:
            pass_to += "?"
        pass_to += "_id=" + eob_id

    print("Calling:", pass_to)

    # Set Context
    context = {'display':"EOB",
               'name': "ExplanationOfBenefit",
               'mask': True,
               'key': key,
               'eob': eob_id,
               'get_fmt': get_fmt,
               'in_fmt': in_fmt,
               'pass_to': pass_to,
               'template': 'v1api/eob.html',
               }

    if settings.DEBUG:
        print("Calling requests with pass_to:", pass_to)

    # We need to replace FHIR Server with External Server reference
    rewrite_from = settings.FHIR_SERVER_CONF['REWRITE_FROM']
    rewrite_to = settings.FHIR_SERVER_CONF['REWRITE_TO']

    try:
        r = requests.get(pass_to)

        context = process_page(request, r, context)

        return publish_page(request, context)

    except requests.ConnectionError:
        pass

    return cms_not_connected(request, 'api:v1:home')


def PatientExplanationOfBenefit(request, patient_id=None, *args, **kwargs):
    """
    Function-based interface to ExplanationOfBenefit
    :param request:
    :return:
    """

    if patient_id == None:
        patient_id = lookup_xwalk(request)

        if patient_id == None:
            err_msg = ['Crosswalk lookup failed: Sorry, We were unable to find',
                       'your record', ]
            exit_message = concat_string("",
                                         msg=err_msg,
                                         delimiter=" ",
                                         last=".")
            messages.error(request, exit_message)
            return kickout_404(exit_message)

    if patient_id == "":
        err_msg = ['Sorry, No Patient Id provided', ]
        exit_message = concat_string("",
                                     msg=err_msg,
                                     delimiter=" ",
                                     last=".")
        messages.error(request, exit_message)
        return HttpResponseRedirect(reverse('api:v1:home'))

    if settings.DEBUG:
        print("In apps.v1api.views.eob.PatientExplanationOfBenefit Function")
        print("request:", request.GET)

    process_mode = request.META['REQUEST_METHOD']

    in_fmt = "json"
    get_fmt = get_format(request.GET)


    if settings.DEBUG:
        print("Request.GET :", request.GET)
        print("KWargs      :", kwargs)
        print("Patient     :", patient_id)

    # We should have the patient_id from xwalk.FHIR_url_id
    # So we will construct the EOB Identifier to include

    # We will deal internally in JSON Format if caller does not choose
    # a format
    in_fmt = "json"
    get_fmt = get_format(request.GET)

    pass_to = FhirServerUrl()
    pass_to += "/ExplanationOfBenefit/"

    key = patient_id
    patient_filter= "?patient=Patient/" + key

    pass_to += patient_filter

    skip_parm = ['_id', '_format']

    pass_to = pass_to + "&" + build_params(request.GET, skip_parm)[1:]

    # Set Context
    context = {'display':"EOB",
               'name': "ExplanationOfBenefit",
               'mask': True,
               'key': key,
               'get_fmt': get_fmt,
               'in_fmt': in_fmt,
               'pass_to': pass_to,
               'template': 'v1api/eob.html',
               }

    if settings.DEBUG:
        print("Calling requests with pass_to:", pass_to)

    try:
        r = requests.get(pass_to)

        context = process_page(request, r, context)

        return publish_page(request, context)

    except requests.ConnectionError:
        pass

    return cms_not_connected(request, 'api:v1:home')
