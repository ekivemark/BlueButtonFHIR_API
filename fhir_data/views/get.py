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
from xml.etree.ElementTree import Element, tostring

from ..utils import (crosswalk_id, dict_to_xml, error_status)
from ..models import ResourceTypeControl

from apps.v1api.utils import build_params
from apps.v1api.views.crosswalk import lookup_xwalk

from fhir.models import SupportedResourceType

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import (HttpResponseRedirect,
                         request,
                         HttpResponse,)
from django.shortcuts import render

from fhir.utils import kickout_404, kickout_400, kickout_500

__author__ = 'Mark Scrimshire:@ekivemark'


def read(request, resource_type, id, *arg, **kwargs):
    """
    Read from remote FHIR Server
    :param resourcetype:
    :param id:
    :return:
    """

    # Check for controls to apply to this resource_type
    if settings.DEBUG:
        print("Resource_Type = ", resource_type)
    rt = SupportedResourceType.objects.get(resource_name=resource_type)
    try:
        srtc = ResourceTypeControl.objects.get(resource_name=rt.id)
    except ResourceTypeControl.DoesNotExist:
        srtc = None

    if settings.DEBUG:
        print('We have Control:', srtc)
        if srtc:
            print("Parameter Rectrictions:", srtc.parameter_restriction())

    if srtc and srtc.force_url_id_override:
        id = crosswalk_id(request, id)

    if settings.DEBUG:
        print("crosswalk:", id)

    if id == None:
        return HttpResponseRedirect(reverse_lazy('api:v1:home'))

    if settings.DEBUG:
        print("now we need to evaluate the parameters and arguments"
              " to work with ", id, "and ", request.user)
        print("GET Parameters:", request.GET, ":")

    key = id.strip()

    in_fmt = "json"
    Txn = {'name': resource_type,
           'display': resource_type,
           'mask': True,
           'server': settings.FHIR_SERVER,
           'locn': "/baseDstu2/"+resource_type+"/",
           'template': 'v1api/%s.html' % resource_type,
           'in_fmt': in_fmt,
           }

    skip_parm = []
    if srtc:
        skip_parm = srtc.parameter_restriction()

    #skip_parm = ['_id',
    #             'access_token', 'client_id', 'response_type', 'state']

    if settings.DEBUG:
        print('Masking the following parameters', skip_parm)
    # access_token can be passed in as a part of OAuth protected request.
    # as can: state=random_state_string&response_type=code&client_id=ABCDEF
    # Remove it before passing url through to FHIR Server

    pass_params = build_params(request.GET, skip_parm)
    if settings.DEBUG:
        print("Parameters:", pass_params)

    pass_to = Txn['server'] + Txn['locn'] + key + "/"

    print("Here is the URL to send, %s now get parameters %s" % (pass_to,pass_params))

    if pass_params != "":
        pass_to = pass_to + pass_params

    # Now make the call to the backend API
    try:
        r = requests.get(pass_to)

    except requests.ConnectionError:
        if settings.DEBUG:
            print("Problem connecting to FHIR Server")
        messages.error(request, "FHIR Server is unreachable." )
        return HttpResponseRedirect(reverse_lazy('api:v1:home'))

    if r.status_code in [301, 302, 400, 403, 404, 500]:
        return error_status(r, r.status_code)

    text_out = ""
    print("r:", r.text)

    if '_format=xml' in pass_params:
        text_out= minidom.parseString(r.text).toprettyxml()
    else:
        text_out = r.json()

    od = OrderedDict()
    od['request_method']= request.method
    od['interaction_type'] = "read"
    od['resource_type']    = resource_type
    od['id'] = id

    if settings.DEBUG:
        print("Query List:", request.META['QUERY_STRING'] )

    od['parameters'] = request.GET.urlencode()

    if settings.DEBUG:
        print("or:", od['parameters'])

    if '_format=xml' in pass_params.lower():
        fmt = "xml"
    elif '_format=json' in pass_params.lower():
        fmt = "json"
    else:
        fmt = ''
    od['format'] = fmt
    od['bundle'] = text_out
    od['note'] = 'This is the %s Pass Thru (%s)\n' % (resource_type,id)

    if settings.DEBUG:
        od['note'] += 'using: %s ' % (pass_to)
        print(od)

    if od['format'] == "xml":
        if settings.DEBUG:
            print("We got xml back in od")
        return HttpResponse( tostring(dict_to_xml('content', od)),
                             content_type="application/%s" % od['format'])
    elif od['format'] == "json":
        if settings.DEBUG:
            print("We got json back in od")
        return HttpResponse(json.dumps(od, indent=4),
                            content_type="application/%s" % od['format'])

    if settings.DEBUG:
        print("We got a different format:%s" % od['format'])
    return render(request,
                  'fhir_data/default.html',
                  {'content': json.dumps(od, indent=4),
                   'output': od},
                  )
