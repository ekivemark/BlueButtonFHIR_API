#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: remote_auth
Created: 1/27/16 4:38 PM

inspiration from:
https://github.com/reddit/reddit/wiki/OAuth2-Python-Example

"""
__author__ = 'Mark Scrimshire:@ekivemark'

import requests
import requests.auth

from urllib.parse import urlencode
from uuid import uuid4

from django.conf import settings
from django.http import HttpResponseRedirect

from ..utils import kickout_403, get_bundle_info
from ..static import REDIRECT_URI, POET_BUNDLE_INFO

def get_authorization(request, bundle):
    """
    prepare the url string for authorization

    :param bundle:
    :return:
    """

    bundle_data = get_bundle_info(bundle)
    #     'POET': {'bundle_ref': "POET001",
    #          'endpoint': "http://localhost:8002/api/entitycheck/",
    #          'token_url': "http://localhost:8002/o/token/",
    #          'authorize_url': "http://localhost:8002/o/authorize",
    #          'client_id': "BBonFHIRclientid",
    #          'client_secret': "BBonFHIRclientsecret",
    #          'token': 'qJt5tH7gPKcaxI7WWJZhzVZpnjMiZz'},

    state = get_or_create_state_token(request)
    bundle_cookie = get_or_create_bundle(request, bundle)

    params = {
        'client_id': bundle_data['client_id'],
        'response_type': 'code',
        'state': state,
        'redirect_uri': REDIRECT_URI,
        'duration': "temporary",
        'scope': "identity"
    }

    authurl = bundle_data['authorize_url'] + "?" + urlencode(params)
    if settings.DEBUG:
        print("Auth URL:", authurl)

    return HttpResponseRedirect(authurl)


def CallBack(request):
    """
    Handle the call back from an authorization link
    :return:
    """

    if settings.DEBUG:
        print("In the callback")
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(get_or_create_state_token(request),state):
        # Problem - This request was not started here!
        kickout_403("Access Forbidden: State mismatch")
    code = request.args.get('code')
    if settings.DEBUG:
        print("Code Returned:", code)

    return get_token(request, code)


def get_token(request, code):
    """
    Get an access token
    :param code:
    :return:
    """
    bundle_data = get_bundle_info(get_or_create_bundle(request))
    client_auth = requests.auth.HTTPBasicAuth(bundle_data['client_id'], bundle_data['client_secret'])
    post_data = {'grant_type': "authorization_code",
                 'code': code,
                 'redirect_uri': REDIRECT_URI,
    }
    response = requests.post(bundle_data['token_url'],
                             auth=client_auth,
                             data=post_data)
    token_json = response.json()
    if settings.DEBUG:
        print("Access_token:", token_json['access_token'])
    return token_json["access_token"]


def get_or_create_state_token(request):
    """
    Create a Unique STATE Cookie
    :param request:
    :return:
    """
    token = request.META.get('POET_STATE_COOKIE', None)
    if token is None:
        token = str(uuid4())
        request.META['POET_STATE_COOKIE'] = token
    request.META['POET_STATE_COOKIE_USED'] = True
    return token


def get_or_create_bundle(request, bundle=""):
    """
    Create a Unique STATE Cookie
    :param request:
    :return:
    """
    token = request.META.get('POET_BUNDLE_COOKIE', None)
    if token is None:
        token = bundle
        request.META['POET_BUNDLE_COOKIE'] = token
    request.META['POET_BUNDLE_COOKIE_USED'] = True
    return token


def is_valid_state(sent_state, received_state):
    if sent_state == received_state:
        return True
    else:
        return False

