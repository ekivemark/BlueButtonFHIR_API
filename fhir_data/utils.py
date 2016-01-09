#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: fhir_data.utils
Created: 1/7/16 11:41 AM

utilities used module-wide

"""
import json

from collections import OrderedDict

from xml.etree.ElementTree import Element, tostring

from apps.v1api.models import Crosswalk

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse

__author__ = 'Mark Scrimshire:@ekivemark'


def concat_string(target, msg=[], delimiter="", last=""):
    """
    Concatenate a series of strings to the end of the target
    Delimiter is optional filler between items
    :param target:
    :param msg:
    :return: target
    """

    result = target

    for m in msg[:-1]:
        result = result + m + delimiter

    result = result + msg[-1] + last

    return result


def crosswalk_id(request, id, element='fhir_url_id'):
    # Lookup up in Crosswalk with request.user
    # First we need to check for AnonymousUser

    if request.user.id == None:
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
        messages.error(request,
                       exit_message)
        return None

    else:
        if settings.DEBUG:
            print("We got a match on ",
                  request.user,
                  ":",
                  xwalk.fhir_url_id)

        return xwalk.fhir_url_id


def dict_to_xml(tag, d):
    '''
    Turn a simple dict of key/value pairs into XML
    '''
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)
    return elem


def error_status(r, status_code=404, reason="undefined error occured"):
    """
    Generate an error page
    based on fhir.utils.kickout_xxx
    :param reason:
    :param status_code:
    :return:
    """
    error_detail = r.text
    if settings.DEBUG:
        if r.text[0] == "<":
            error_detail = "xml:"
            error_detail += r.text
        else:
            error_detail = r.json()

    response= OrderedDict()

    response["errors"] = [reason, error_detail]
    response["code"] = status_code

    return HttpResponse(json.dumps(response, indent = 4),
                        status=status_code,
                        content_type="application/json")
