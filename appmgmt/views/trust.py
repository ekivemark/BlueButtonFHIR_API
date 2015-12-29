"""
bofhirdev.apps.appmgmt
FILE: views.py
Created: 10/28/15 5:20pm

"""

import datetime
import random
import requests

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

from appmgmt.forms.trust import TrustForm
from appmgmt.models import Organization

# We need an app management set of transactions here

# Change test line to point to localhost:port
BUNDLE_INFO = {
    'TEST': {'bundle_ref': "T001",
             'endpoint': "/appmanagement/trust_test/",
             'client_id': "1234567890",
             'token': 'x12345678'},
    'NATE': {'bundle_ref': "N001",
             'endpoint': "https://api.nate.org/trust_test/",
             'client_id': "1234567890",
             'token': 'x12345678'},
    'DIRECTTRUST': {'bundle_ref': "DT001",
             'endpoint': "https://api.directtrust.org/trust_test/",
             'client_id': "9876543210",
             'token': 'x87654321'}
}

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

    # Get dictionary from BUNDLE_INFO dict using bundle as key
    # lookup bundle in dictionary
    # get access parameters for call to api endpoint

    trust_info = {}
    if not bundle.upper() in BUNDLE_INFO:
        messages.error(request, "Invalid information provided")
        valid = False
        return {'trust_info': trust_info, 'valid': valid}
    else:
        api_call = BUNDLE_INFO[bundle.upper()]
        bundle_id = api_call['bundle_ref']
        if settings.DEBUG:
            print("We got the bundle", api_call)
    # We have a valid bundle dictionary
    # make api call with dictionary

    if bundle.upper() == "TEST":
        if settings.DEBUG:
            print("URL_PRE:", settings.URL_PRE,
                  " get_host():", request.get_host(),
                  "updated ", bundle.upper(),
                  " endpoint to ", api_call['endpoint'])

        if settings.URL_PRE + request.get_host() in api_call['endpoint']:
            # We have a full url in api_call['endpoint']
            pass
        else:
            # We are missing the http(s)://[host] in api_call['endpoint']
            # so add as a prefix
            api_call['endpoint'] = settings.URL_PRE + request.get_host() + api_call['endpoint']

    Base_Trust = {
                 "requested_by": requester_email,
                 "bundle": bundle_id,
                 "domain": domain,
                 "owner": owner_email,
                 "shared_secret": shared_secret,
    }

    if settings.DEBUG:
        print("calling", api_call['endpoint'], "with", Base_Trust)
    # Make POST call to endpoint with BaseTrust dictionary as payload

    print("Running on:",request.get_host())

    try:
        r = requests.get(api_call['endpoint'], data=Base_Trust)
        result = r.status_code
        # trust_info = r.json()

        if settings.DEBUG:
            print("Result from Trust API Call:", result)
            print("Returned json:", trust_info)
        # result = 200

        if result == 200:
            valid = True

            trust_info = r.json()

            messages.info(request, "Trust Bundle Validation succeeded")
            messages.info(request, "Trust valid until %s" % trust_info['expires'])

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
                                        RequestContext(request, valid,
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

    if settings.DEBUG:
        print("User (u):", u)

    if request.method == 'POST':

        form = TrustForm(request.POST)
        if form.is_valid():

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
                until_dt = datetime.strptime(trust_info['expires'],
                                             '%Y%m%d.%H%M').replace(tzinfo=tz)
                org.trusted_until = until_dt
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
