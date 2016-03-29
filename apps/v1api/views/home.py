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

from xml.etree import ElementTree

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe

from bbapi.utils import FhirServerUrl
from fhir.utils import kickout_404

from apps.v1api.models import Crosswalk
from apps.v1api.utils import get_format
from apps.v1api.views.patient import (process_page,
                                      publish_page)

# Create your views here.

@login_required
def api_index(request):
    # Show API/v1 Home Page

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE, "in apps.api.views.api_index")

    if "_getpages" in request.GET and request.user.is_authenticated():
        return next_search(request)
        # Call FHIR Server with GET Args

    if request.user.is_authenticated():
        c = Crosswalk.objects.get(user=request.user)
    else:
        c = ""

    context = {"crosswalk": c,}
    return render_to_response('v1api/index.html',
                              RequestContext(request, context, ))


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
