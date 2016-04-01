"""
bbofuser: apps.v1api
FILE: views.py
Created: 8/6/15 6:34 PM

Views for V1 of REST API
i.e. [Server_root]/api/v1/

"""
__author__ = 'Mark Scrimshire:@ekivemark'

import json

import requests
import xml.dom.minidom

from collections import OrderedDict
from xml.etree import ElementTree

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe

from bbapi.utils import FhirServerUrl
from fhir.utils import kickout_404

from apps.setup.views import get_page_content
from apps.v1api.models import Crosswalk
from apps.v1api.utils import get_format
from apps.v1api.views.patient import (process_page,
                                      publish_page)


@login_required
def api_index(request):
    # Show API/v1 Home Page

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE, "in apps.api.views.api_index")

    if "_getpages" in request.GET and request.user.is_authenticated():
        return next_search(request)
        # Call FHIR Server with GET Args

    patient_count = get_patient_count()
    eob_count = get_eob_count()
    if request.user.is_authenticated():
        c = Crosswalk.objects.get(user=request.user)
    else:
        c = ""


    my_eob_count = get_my_eob_count(c.fhir_url_id)

    context = {"crosswalk": c,
               "patient_count": patient_count,
               "eob_count": eob_count,
               "my_eob_count": my_eob_count}

    return render_to_response('v1api/index.html',
                              RequestContext(request, context, ))


def fhir_metadata(request):
    """"
    fhir conformance statement

    """

    # prototype output

    conform = OrderedDict()
    conform['resourceType'] = "Conformance"
    conform['url'] = settings.URL_PRE + settings.DOMAIN
    conform['version'] = settings.VERSION_INFO
    conform['name'] = "CMS Blue Button Data API"
    conform['status'] = "draft"
    conform['experimental'] = True
    conform['Publisher'] = "Centers for Medicare and Medicaid Services, " \
                           "Office of Enterprise Data Analytics"

    conform['implementation'] = { "description": "BBonFIR_API:Experimental API "
                                                 "with synthetic data.",
                                  "url": "/api/v1" },

    conform['fhirVersion'] = "2.11"
    conform['format'] = ["json", "xml"]

    return HttpResponse(json.dumps(conform, indent=4),
                        content_type="application/json")


def next_search(request, *args, **kwargs):
    """
    Handle search requests
    :param request:
    :return:
    """

    server = FhirServerUrl()
    in_fmt = "json"
    get_fmt = get_format(request.GET)

    if settings.DEBUG:
        print("Server:", server)
        print("Kwargs:",kwargs)

    context = {'display':"Search",
               'name': "Search",
               'server': server,
               'in_fmt': in_fmt,
               'get_fmt': get_fmt,
               'template': 'v1api/search.html',
               }

    request_string = "?"
    for item in request.GET:
        request_string += item +"=" + request.GET[item] +"&"

    if request_string[:0] =="&":
        request_string = request_string[:-1]

    if not "patient=Patient/" in request_string:
        try:
            xwalk = Crosswalk.objects.get(user=request.user)
            patient_id = xwalk.fhir_url_id
            request_string += "&patient=Patient/"+patient_id
        except Crosswalk.DoesNotExist:
            return kickout_404("ID for this user not found:%s" % request.user)

    if settings.DEBUG:
        print("Gets:", request_string)

    try:
        r = requests.get(server+request_string)

        context = process_page(request, r, context)

        return publish_page(request, context)


    except requests.ConnectionError:
        print("Whoops - Problem connecting to FHIR Server")
        messages.error(request,
                       "FHIR Server is unreachable. "
                       "Are you on the CMS Network?")

    return render_to_response(context['template'],
                              RequestContext(request, context, ))


def get_patient_count():
    """
    Do patient search and get total field for number of patients
    """

    total = get_api_count("/Patient?_format=json")

    return total


def get_eob_count():
    """
    Do ExplanatinOfBenefit search and get total field for number of EOBs
    """

    total = get_api_count("/ExplanationOfBenefit?_format=json")

    return total


def get_my_eob_count(id):
    """
    Do a search for a Patient's EOB Count
    """

    total = get_api_count("/ExplanationOfBenefit?_format=json&patient=Patient/"+id)

    return total


def get_api_count(api_parm):
    """
    Generic API Call to a search to get count
    """

    server = FhirServerUrl() + api_parm

    j = get_page_content(server)

    if 'total' in j:
        return j['total']

    else:
        return None