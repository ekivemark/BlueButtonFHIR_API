"""
bofhirdev.apps.appmgmt
FILE: views.py
Created: 10/28/15 5:20pm

"""

import datetime
import json
import oauth2 as oauth
import random
import requests
import time
import urllib.parse as urlparse

from collections import OrderedDict

from django.conf import settings
from django.contrib.auth import get_user_model

from datetime import datetime, date, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import (HttpResponse,
                         JsonResponse,
                         HttpResponseRedirect)
from django.shortcuts import (render, render_to_response)
from django.template import RequestContext
from django.utils.timezone import get_current_timezone
from django.utils.dateparse import parse_datetime

from appmgmt.forms.trust import TrustForm
from appmgmt.models import Organization

from .poet import get_authorization
from ..utils import get_bundle_info

from ..static import REDIRECT_URI, POET_BUNDLE_INFO


@login_required()
def BaseTrust(request, requester_email,
              bundle, domain, owner_email,
              shared_secret="",
              internal_call=False):
    """

    Implement an API call to check if Domain and Owner_email
    is in trust bundle

    success returns 200 OK
    failure returns 404 Not Found

    :param request:
    :param requestor_email
    :param bundle:
    :param domain:
    :param owner_email:
    :param shared_secret:
    :return:
    """

    valid = False

    # Get dictionary from POET_BUNDLE_INFO dict using bundle as key
    # lookup bundle in dictionary
    # get access parameters for call to api endpoint

    trust_info = {}
    if not bundle.upper() in POET_BUNDLE_INFO:
        messages.error(request, "Invalid information provided")
        valid = False
        return {'trust_info': trust_info, 'valid': valid}
    else:
        api_call = POET_BUNDLE_INFO[bundle.upper()]
        bundle_id = api_call['bundle_ref']
        if settings.DEBUG:
            print("We got the bundle", api_call)

    Base_Trust = {
                 "requested_by": requester_email,
                 "bundle": bundle_id,
                 "domain": domain,
                 "owner": owner_email,
                 "shared_secret": shared_secret,
    }

    if settings.DEBUG:
        print("Registering with POET API", api_call['token_url'])

    my_csrftoken = request.META.get('CSRF_COOKIE', None)

    Base_Trust['csrftoken'] = my_csrftoken

    headers = {"Authorization": 'Bearer ' + api_call['token'],
               "scope": 'write',
               "Content-Type": 'application/json',
               "X-CSRFToken": my_csrftoken,
               "Referer": api_call['token_url']
               }

    # registration = OAuthRegister(request, bundle)

    if settings.DEBUG:
        print("calling", api_call['endpoint'], "with", Base_Trust)
    # Make POST call to endpoint with BaseTrust dictionary as payload

    print("Running on:",request.get_host())

    try:
        r = requests.post(api_call['endpoint'], headers=headers, data=json.dumps(Base_Trust))
        result = r.status_code
        # trust_info = r.json()

        if settings.DEBUG:
            print("Result from Trust API Call:", result)
            print("Returned json:", r.text)
        # result = 200

        if result == 200:
            valid = True
            print("text:", r.text)
            trust_info = r.json()

            messages.info(request, "Trust Bundle Validation succeeded")
            messages.info(request, "Trust valid since %s" % trust_info['joined_bundle'])

        if result == 403:
            valid = False
            messages.error(request, "403: Not Authorized")
            trust_info = {}

        if result == 404:
            valid = False
            messages.error(request, "Failed Trust bundle validation")
            trust_info = {}

    except requests.ConnectionError:
        messages.error(request,"We had a problem reaching the endpoint")
        valid = False

    if internal_call:
        # Return without doing a redirect
        return {'valid': valid, 'trust_info': trust_info}

    return HttpResponseRedirect(reverse('home'),
                                RequestContext(request,
                                               valid,
                                               trust_info))


@login_required()
def TrustData(request):
    """
    Get data to use for BaseTrust call:
        requester_email (from user.email),
        bundle,
        domain,
        owner_email

    :param request:
    :param user: logged in user
    :param organization:  Organization Name

    :return:
    """

    user = get_user_model()
    access_field = settings.USERNAME_FIELD

    print("User:", user)
    print("User(email):",request.user.email)

    u = user.objects.filter(**{access_field: request.user})

    poetconf = getattr(settings, 'POET_CONF', {'MODE':"CHECK"})
    poet_mode = poetconf['MODE']

    if settings.DEBUG:
        print("User (u):", u)
        print("POET MODE:", poet_mode)

    if poet_mode == "AUTO_TRUST":
        # Set to trusted and current date/time and return
        org = Organization.objects.get(owner=request.user)
        org.trusted = True
        org.trusted_since = datetime.now()
        org.save()
        return HttpResponseRedirect(reverse('appmgmt:organization_view'))

        # No AUTO_TRUST so we process the form.
        if settings.DEBUG:
            print("AUTO TRUSTED Organization:", org.name)

    if request.method == 'POST':

        form = TrustForm(request.POST)
        if form.is_valid():

            if settings.DEBUG:
                print("Valid Trust Form. Calling BaseTrust")
            # trust_bundle = forms.ChoiceField(choices=TRUST_BUNDLE_CHOICE)
            # trust_domain = forms.CharField(max_length=100,label="Trusted Application Domain")
            # owner_email = forms.EmailField(label="Trusted Application Owner Email")

            whitelist = BaseTrust(request,
                                  request.user.email,
                                  form.cleaned_data['trust_bundle'],
                                  form.cleaned_data['trust_domain'],
                                  form.cleaned_data['owner_email'],
                                  form.cleaned_data['shared_secret'],
                                  internal_call=True)

            if settings.DEBUG:
                print("Whitelist result:", whitelist)

            org = Organization.objects.get(owner=request.user)
            if whitelist['valid']:
                trust_info = whitelist['trust_info']
                org.trusted = whitelist['valid']
                tz = get_current_timezone()
                since_dt = parse_datetime(trust_info['validation_timestamp'])
                # since_dt = datetime.strptime(trust_info['validation_timestamp'],
                #                              '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=tz)
                org.trusted_since = since_dt
                org.save()

            if settings.DEBUG:
                print("Org:", org, ":", org.trusted)

            return HttpResponseRedirect(reverse('appmgmt:organization_view'))
    else:
        # t=u.objects.get(**{access_field: request.user})
        t = {'trust_bundle': "",
             'trust_domain': "",
             'administrator_email': ""}

        if settings.DEBUG:
            print("T:", t)
        form = TrustForm()
        return render(request,
                      'appmgmt/trust_form.html',
                      {'form': form})

    return HttpResponseRedirect(reverse('accounts:manage_account'))

###########################################################################
###########################################################################
###########################################################################


def TrustTest(data):
    """
    Test for Trust api

    This is used to randomly return 200 or 404 to BaseTrust

    Return 404 or 200

    :return:
    """

    if settings.DEBUG:
        print("Made the call to TrustTest")

    ret_options = [[200, "Ok"],[404, "Not Found"]]

    ret_val = random.choice(ret_options)

    now = datetime.now()
    then = now + timedelta(days=365)
    expires= then.strftime("%Y%m%d.%H%M")

    if settings.DEBUG:
        print("now:", now)
        print("then:", then)
        print("Expires:", expires)
        print("Randomly selected:", ret_val[0], ret_val[1])

    result = {"result": ret_val[1]}

    if ret_val[0] == 200:
        result['expires'] = expires

    if settings.DEBUG:
        print("Result:", result)

    response = JsonResponse(result)
    response.status_code = ret_val[0]
    return response


def OAuthRegister(request, bundle=""):
    """
    Get the bundle and register the endpoint using the client_id

    :param bundle:
    :return:
    """

    od = OrderedDict()
    if bundle == "":
        # No bundle so return
        return od

    bundle_data = {}
    bundle_data = get_bundle_info(bundle)
    if settings.DEBUG:
        print("type for bundle_data", type(bundle_data))

    if bundle_data == {}:
        # Empty Dict so return
        return od

    # We have a BUNDLE Let's register the service
    #     'POET': {'bundle_ref': "POET001",
    #              'endpoint': "http://localhost:8002/api/entitycheck/",
    #              'token_url': "http://localhost:8002/o/token/",
    #              'client_id': "BBonFHIRclientid",
    #              'client_secret': "BBonFHIRclientsecret",
    #              'token': 'x12345678'},

    result = get_authorization(request, bundle)

    if settings.DEBUG:
        print("Result from get_authorization:", result)

    consumer = oauth.Consumer(key=bundle_data['client_id'],
                              secret=bundle_data['client_secret'])

    token = oauth.Token(key=bundle_data['token'],secret="")

    params = {
        'oauth_version': "2.0",
        'oauh_nonce': oauth.generate_nonce(),
        'oauth_timestamp': str(int(time.time())),
        'user': 'cms',
    }

    url = bundle_data['endpoint']

    params['oauth_token'] = token.key
    params['oauth_consumer_key'] = consumer.key

    req = oauth.Request(method="POST", url=url, parameters= params)
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, token)


    # request_token_url = bundle_data['token_url']
    #
    # client = oauth.Client(consumer, token)

    # resp, content = client.request(access_token_url, "POST")
    # print("Response:", resp)
    # print('Content:', content)

    print("req:", req)

    od = OrderedDict()
    # od['resp'] = resp
    # od['content'] = content

    return req


