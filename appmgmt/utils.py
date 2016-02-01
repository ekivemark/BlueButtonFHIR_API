# -*- coding: utf-8 -*-
"""
BlueButtonDev.appmgmt
FILE: utils
Created: 12/2/15 8:09 PM

"""
__author__ = 'Mark Scrimshire:@ekivemark'

import json

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