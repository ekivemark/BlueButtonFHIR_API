#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
django-fhir
FILE: get
Created: 1/6/16 5:08 PM


"""
import json
import requests

from collections import OrderedDict
from xml.dom import minidom

from django.contrib import messages

from apps.v1api.utils import build_params
from apps.v1api.views.crosswalk import lookup_xwalk

__author__ = 'Mark Scrimshire:@ekivemark'


from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import (HttpResponseRedirect,
                         request,
                         HttpResponse)


def read(request, resource_type, id, *arg, **kwargs):
    """
    Read from remote FHIR Server
    :param resourcetype:
    :param id:
    :return:
    """

    xwalk_id = lookup_xwalk(request, )
    if settings.DEBUG:
        print("crosswalk:", xwalk_id)

    if xwalk_id == None:
        return HttpResponseRedirect(reverse_lazy('api:v1:home'))

    if settings.DEBUG:
        print("now we need to evaluate the parameters and arguments"
              " to work with ", xwalk_id, "and ", request.user)
        print("GET Parameters:", request.GET, ":")

    if id == xwalk_id:
        key = id
    else:
        key = xwalk_id.strip()

    in_fmt = "json"
    Txn = {'name': resource_type,
           'display': resource_type,
           'mask': True,
           'server': settings.FHIR_SERVER,
           'locn': "/baseDstu2/"+resource_type+"/",
           'template': 'v1api/patient.html',
           'in_fmt': in_fmt,
           }

    skip_parm = ['_id',
                 'access_token', 'client_id', 'response_type', 'state']

    # access_token can be passed in as a part of OAuth protected request.
    # as can: state=random_state_string&response_type=code&client_id=ABCDEF
    # Remove it before passing url through to FHIR Server

    pass_params = build_params(request.GET, skip_parm)
    if settings.DEBUG:
        print("Parameters:", pass_params)

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
    if '_format=xml' in pass_params:
        text_out= minidom.parseString(r.text).toprettyxml()
    else:
        text_out = r.json()

    od = OrderedDict()
    od['request_method']= request.method
    od['interaction_type'] = "read"
    od['resource_type']    = resource_type
    od['id'] = id
    od['parameters'] = request.GET

    if '_format=xml' in pass_params.lower():
        fmt = "xml"
    elif '_format=json' in pass_params.lower():
        fmt = "json"
    else:
        fmt = 'json'
    od['format'] = fmt
    od['bundle'] = text_out
    od['note'] = 'This is the Patient Pass Thru %s using %s ' % (xwalk_id, pass_to)

    if settings.DEBUG:
        print(od)

    return od
