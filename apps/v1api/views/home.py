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
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

from django.shortcuts import render, render_to_response
from django.template import RequestContext

from apps.v1api.models import Crosswalk


# TODO: Setup DJANGO REST Framework
# DONE: Apply user scope to FHIR Pass through
# DONE: Test Pass through to FHIR Server
# DONE: Create api:vi namespace in urls.py.py
# TODO: Detect url of accessing apps. Store in Connected_from of Device field
# TODO: Extract site domain from querying url in Connected_From

# Create your views here.


def api_index(request):
    # Show API/v1 Home Page

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE, "in apps.api.views.api_index")

    if request.user.is_authenticated():
        c = Crosswalk.objects.get(user=request.user)
    else:
        c = ""

    context = {"crosswalk": c,}
    from django.template import RequestContext
    return render_to_response('v1api/index.html',
                              RequestContext(request, context, ))



