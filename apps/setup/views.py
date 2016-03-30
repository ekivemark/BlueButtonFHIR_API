#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: views
Created: 3/8/16 1:45 AM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

import datetime
import json
import random
import requests
import string

from collections import OrderedDict
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse_lazy

from django.http import (HttpResponse,
                         HttpResponseRedirect)

from bbapi.utils import FhirServerUrl, notNone

from fhir.utils import (kickout_301,
                        kickout_400,
                        kickout_401,
                        kickout_403,
                        kickout_404,
                        kickout_500,
                        kickout_502,
                        kickout_504)
from fhir_io_hapi.utils import (error_status)

from accounts.models import User
from apps.v1api.models import Crosswalk
from apps.v1api.views.patient import re_write_url


@staff_member_required
def getpatient(request):

    if settings.DEBUG:
        print("in getpatient")


    od = OrderedDict()
    # Compile call to Patient search on FHIR Server

    od['fhir_server'] = FhirServerUrl() + "/" + "Patient"
    od['count'] = 10
    od['parameters'] = "?_format=json&_count=" + str(od['count'])

    # set count to 10 to return 10 items per page

    j = get_page_content(od['fhir_server'] + od['parameters'])

    if 'total' in j:
        od['total'] = j['total']
    else:
        od['total'] = 0

    then = datetime.datetime.now()
    od['start'] = str(then)
    if 'entry' in j:
        od['entries'] = len(j['entry'])
    else:
        od['entries'] = 0
    od['entry'] = []
    if settings.DEBUG:
        print("od:", od)
        # print("j:", j)

    if settings.DEBUG:
        print("Entries:", od['entries'])
    # Now we have the number of entries
    # and the contents of the entries

    # pass the content, current count and total to function to get patient info
    bundle_count = od['entries']
    rt = 0
    while rt < od['total']:
        x = 0
        while x < notNone(bundle_count,0):
            if settings.DEBUG:
                # Print every 100 lines
                if x % 100 == 0:
                    print("running for:", datetime.datetime.now()-then)
                    print("x:", rt+x)
                    print("OD:", od)
                    # print("entries:", len(j['entry']))
            if 'entry' in j:
                result = extract_info(j['entry'][x])
                od['entry'].append(result['id'])
            x += 1

            if x >= notNone(bundle_count,0):
                # We need to request the next page
                next_page = get_next_page(j)
                if next_page != "":
                    j = get_page_content(next_page)
                    if 'entry' in j:
                        bundle_count = len(j['entry'])
        rt += x
        # if settings.DEBUG:
        #     print("rt:", rt)

    od['result'] = str(j)
    now = datetime.datetime.now()
    od['end'] = str(then)
    od['elapsed'] = str(now - then)
    od['processed'] = rt
    # Check total

    # while x <= 10 and y <= total

    # get Patient from entity
    # get fhir url id
    # get name
    # get identifier

    # update crosswalk
    # update user account

    # Increment count while count less than total

    if settings.DEBUG:
        print("OD -result:",od['result'])
    return HttpResponse(json.dumps(od, indent=4),
                            content_type="application/json")


def geteob(request):
    """
    Process each crosswalk record.
    Get the fhir_url_id
    Construct an ExplanationOfBenefit call using patient=Patient/{xwalk.fhir_url_id}
    Get the count
    Write to xwalk.eob_cont
    """

    server_call = FhirServerUrl() + "/ExplanationOfBenefit/?_format=json&patient=Patient/"

    ctr = 0
    od = OrderedDict()
    od['server'] = FhirServerUrl()
    od['api_call'] = "/setup/geteob"
    then = datetime.datetime.now()
    od['start'] = str(then)

    for x in Crosswalk.objects.all():
        patient_id = x.fhir_url_id

        u = server_call + patient_id

        j = get_page_content(u)

        if 'total' in j:
            x.eob_count = notNone(j["total"],0)
        x.save()
        ctr += 1
        if ctr % 100 == 0:
            print("processed ", ctr)
            print("elapsed ", str(datetime.datetime.now()-then))

    od['processed'] = ctr
    now = datetime.datetime.now()
    od['elapsed'] = str(now - then)
    od['end'] = str(now)

    return HttpResponse(json.dumps(od, indent=4),
                        content_type="application/json")


def get_next_page(j):
    # Get the next page

    next_page = ""
    # print("Get Next Page from link:", json.dumps(j, indent=4))
    for l in j['link']:
        if l['relation'] == "next":

            next_page = FhirServerUrl() + "?" + l['url'].split("?")[1]

    return next_page


def get_page_content(u):
    # Call the page and return the result

    try:
        r = requests.get(u)

    except requests.ConnectionError:
        if settings.DEBUG:
            print("Problem connecting to FHIR Server")
            print("called:", u)
        return HttpResponseRedirect(reverse_lazy('api:v1:home'))

    # test for errors:
    if r.status_code in [301, 302, 400, 403, 404, 500, 502, 504]:
        return error_status(r, r.status_code)

    pre_text = re_write_url(r.text)
    try:
        j =json.loads(pre_text, object_pairs_hook=OrderedDict)
    except ValueError:
        if settings.DEBUG:
            print("Problem with:", u)
            print("returned:", pre_text)
        j = {}

    return j


def extract_info(item):
    # Extract the Patient Entry

    e = OrderedDict()

    this = item
    # print("this item:", this)
    resource = this['resource']

    e['id'] = resource['id']
    e['identifier'] = resource['identifier'][0]['value']
    if 'name' in resource:
        e['first_name'] = resource['name'][0]['given'][0]
        e['last_name'] = resource['name'][0]['family'][0]
    if 'telecom' in resource:
        e['phone'] = resource['telecom'][0]['value']
        e['email'] = resource['telecom'][1]['value']

    e['user'] = write_user_account(e)

    return e


def write_user_account(e):
    # Write user record

    # user-name = "U" + e['id']
    # password = "P" + e['id']
    # ## u.set_password('new password')
    # email_address = e['email']
    # first_name
    # last_name
    # is_active = True
    # is_user = True

    rand_str_first = ''.join(random.sample(string.ascii_lowercase, 6))
    rand_str_last = ''.join(random.sample(string.ascii_lowercase, 8))

    # print(rand_str)
    try:
        u = User.objects.get(username="u"+e['id'])
        # if settings.DEBUG:
        #    print("Updating:", "u"+e['id'])
        if 'email'in e:
            u.email = rand_str +"."+ e['email']
        if 'first_name' in e:
            u.first_name = e['first_name']
        else:
            u.first_name = ""
        if 'last_name' in e:
            u.last_name = e['last_name']
        else:
            u.last_name = ""
        u.set_password('p'+e['id'])
    except User.DoesNotExist:
        if 'first_name' in e:
            first_name = e['first_name']
        else:
            first_name = ""
        if 'last_name' in e:
            last_name = e['last_name']
        else:
            last_name = ""

        if 'email' in e:
            rand_email = rand_str +"."+ e['email']
        else:
            rand_email = rand_str_first + rand_str_last+ "@example.com"

        u = User.objects.create_user(username="u"+e['id'],
                                     email=rand_email,
                                     first_name=first_name,
                                     last_name=last_name,
                                     password='p'+e['id'])

    if 'email' in e:
        u.email = rand_str +"."+ e['email']
    else:
        u.email = rand_str +".unknown@example.com"
    u.is_active = True
    u.is_user = True
    u.is_developer = False

    u.save()

    # write Crosswalk

    try:
        c = Crosswalk.objects.get(user=u)
        c.fhir_url_id = e['id']
        # c.eob_count = get_eob_count(e)
        c.save()
        # if settings.DEBUG:
        #    print("Updating Crosswalk:",c.user)

    except Crosswalk.DoesNotExist:
        c = Crosswalk.objects.create(user=u, fhir_url_id=e['id'])
        # if settings.DEBUG:
        #    print("Creating Crosswalk:", c.user)

    return u.username+",p" + e['id']+","+u.email


def get_eob_count(e):
    """
    Do EOB Search for patient=Patient/{e['id']}
    Get count
    """

    pass_to  = FhirServerUrl() + "/" +"ExplanationOfBenefit"
    pass_to += "?_format=json&patient=Patient/"
    pass_to += e['id']

    eob = get_page_content(pass_to)

    # eob search bundle returnedin json format

    eob_count = notNone(eob['total'], 0)

    return eob_count

