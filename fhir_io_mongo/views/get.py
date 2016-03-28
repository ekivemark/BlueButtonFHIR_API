#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: django-fhir.fhir_io_mongo.views.get
Created: 1/9/16 3:57 PM


"""
import json

from collections import OrderedDict

from django.http import HttpResponse

# Replace next line with
DF_EXTRA_INFO = False
# this line when development is complete
#from fhir.settings import DF_EXTRA_INFO

__author__ = 'Mark Scrimshire:@ekivemark'


def hello_world(request, resource_type, id, *arg, **kwargs):
    """
    Simple Hello World to check for pluggable module
    :param request:
    :param resource_type:
    :param id:
    :param arg:
    :param kwargs:
    :return:
    """
    return "Hello World from fhir_io_mongo.views.get.hello_world: " \
           "%s,{%s}[%s]" % (request,
                            resource_type,
                            id)


def read(request, resource_type, id, *arg, **kwargs):
    """
    Read from remote FHIR Server
    :param resourcetype:
    :param id:
    :return:
    """

    od = OrderedDict()
    if DF_EXTRA_INFO:
        od['request_method']= request.method
        od['interaction_type'] = "search"
    od['resource_type']    = resource_type
    if DF_EXTRA_INFO:
        od['search_params'] = request.GET
        od['note'] = "This is only a stub for future implementation of " \
                     "MongoDB as a pluggable module for django-fhir." \
                     "Suppress this message by setting DF_EXTRA_INFO = False  " \
                     "in fhir_io_mongo.views.get.py"


    return HttpResponse(json.dumps(od, indent=4),
                        content_type="application/json")
