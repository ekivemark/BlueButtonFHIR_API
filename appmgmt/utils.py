# -*- coding: utf-8 -*-
"""
BlueButtonDev.appmgmt
FILE: utils
Created: 12/2/15 8:09 PM

"""
__author__ = 'Mark Scrimshire:@ekivemark'

import json
import requests

from collections import OrderedDict
from django.contrib import messages
from django.http import HttpResponse

from accounts.choices import DEVELOPER_ROLE_CHOICES

from django.conf import settings

from .static import POET_BUNDLE_INFO


def Choice_Display(role):
    """
    Receive a string of the current role
    Lookup in DEVELOPER_ROLE_CHOICES
    Return the String
    :param role:
    :return:
    """
    result = dict(DEVELOPER_ROLE_CHOICES).get(role)

    if role == "None":

        return
    else:
        return result


class MessageMixin(object):
    """
    Make it easy to display notification messages when using Class Based Views.
    """
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).delete(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).form_valid(form)


def kickout_403(reason, status_code=403):
    response= OrderedDict()
    response["code"] = status_code
    response["errors"] = [reason,]
    return HttpResponse(json.dumps(response, indent = 4),
                        status=status_code,
                        content_type="application/json")


def get_bundle_info(bundle=""):
    """
    Get Bundle info from BUNDLE_INFO
    :param bundle:
    :return:
    """

    if bundle=="":
        # nothing in return empty dict
        return {}

    if not bundle.upper() in POET_BUNDLE_INFO:
        # No match so return empty dict
        return {}

    # Get the bundle
    api_call = POET_BUNDLE_INFO[bundle.upper()]
    if settings.DEBUG:
        print("API_Call Type:", type(api_call))
        print("API Call Dict:", api_call)
    return api_call


def write_fhir(mode, resource, body, target ):
    """ write a record to FHIR
    :return:
    """

    result = ""
    headers = {'content-type': 'application/json+fhir;charset=UTF-8'}

    if mode == "PUT" and target != "":
        server = settings.FHIR_SERVER + "/baseDstu2/" + target
    else:
        server = settings.FHIR_SERVER + "/baseDstu2/"+resource

    server = server + "?_format=json"

    if settings.DEBUG:
        print("in write_fhir:", server, mode, resource, body)

    if mode == "POST":
        r = requests.post(server, data=body, headers=headers)
    else:
        # mode == "PUT"
        r = requests.put(server, data=body, headers=headers)

    if r.status_code == 200 or r.status_code == 201:
        # We need to strip the url down to "{Resource}/{number}
        result = get_resource_number(r.headers['Location'], resource)

    else:
        result = target


    if settings.DEBUG:
        print("Result:", r.status_code, r.text, result)
        print("URL:", r.url)
        print("Headers:", r.headers)
        print(r.json)

    return result

"""
{"resourceType": "Organization",
 "identifier": {"value": 2,
                "system": "dev.bbonfhir.com",
                "type": "Organization"},
 "type": {"text": "Developer Organization"},
 "name": "Medyear",
 "telecom": [{"resourceType": "ContactPoint",
              "value": "http://Medyear.com",
              "system": "domain"}]
}


{"resourceType": "Organization", "identifier": {"system": "dev.bbonfhir.com", "type": "Organization", "value": 2}, "type": {"text": "Developer Organization"}, "name": "Medyear", "telecom": [{"resourceType": "ContactPoint", "system": "domain", "value": "http://Medyear.com"}]}

"""


def get_resource_number(location, resource):
    """
    Get {Resource}/{Number} from _history url

    eg. http://ec2-52-4-198-86.compute-1.amazonaws.com:8080/baseDstu2/Organization/4995667/_history/1

    :param location:
    :param resource:
    :return:
    """
    result = ""

    leftstrip = location.find(resource)
    rightstrip = location.find("/_history/")
    if rightstrip >0:
        result = location[leftstrip:rightstrip]
    else:
        result = location[leftstrip:]

    if settings.DEBUG:
        print("location:", location)
        print("Resource:", resource)
        print("left:", leftstrip,
              "right:", rightstrip)
        print("result:", result)

    return result


def build_fhir_id(key1, value1, key2, value2, key3, value3):
    """
    Construct an OrderedDict for ID
    :param key1:
    :param value1:
    :param key2:
    :param value2:
    :param key3:
    :param value3:
    :return:
    """

    id_info = OrderedDict()
    id_info[key1] = value1
    id_info[key2] = value2
    id_info[key3] = value3

    return id_info
