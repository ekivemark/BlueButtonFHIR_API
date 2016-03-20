#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: views
Created: 3/8/16 1:45 AM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

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
from fhir_io_hapi.utils import (build_fhir_server_url,
                                error_status)

from accounts.models import User
from apps.v1api.models import Crosswalk


@staff_member_required
def getpatient(request):

    if settings.DEBUG:
        print("in getpatient")


    od = OrderedDict()
    # Compile call to Patient search on FHIR Server

    od['fhir_server'] = build_fhir_server_url(release=True) + "Patient"
    od['count'] = 10
    od['parameters'] = "?_format=json&_count=" + str(od['count'])

    # set count to 10 to return 10 items per page

    j = get_page_content(od['fhir_server'] + od['parameters'])

    od['total'] = j['total']

    od['entries'] = len(j['entry'])
    od['entry'] = []

    if settings.DEBUG:
        print("Entries:", len(j['entry']))
    # Now we have the number of entries
    # and the contents of the entries

    # pass the content, current count and total to function to get patient info

    rt = 0
    while rt < od['total']:
        x = 0
        while x < len(j['entry']):
            if settings.DEBUG:
                print("x:", x)
                print("entries:", len(j['entry']))

            od['entry'].append(extract_info(j['entry'][x]))
            x += 1

            if x >= len(j['entry']):
                # We need to request the next page
                next_page = get_next_page(j)
                if next_page != "":
                    j = get_page_content(next_page)

        rt = rt + x
        print("rt:", rt)

    od['result'] = j
    # Check total

    # while x <= 10 and y <= total

    # get Patient from entity
    # get fhir url id
    # get name
    # get identifier

    # update crosswalk
    # update user account

    # Increment count while count less than total

    return HttpResponse(json.dumps(od, indent=4),
                            content_type="application/json")


def get_next_page(j):
    # Get the next page

    next_page = ""

    for l in j['link']:
        if l['relation'] == "next":

            next_page = build_fhir_server_url(release=True) + "?" + l['url'].split("?")[1]

    return next_page


def get_page_content(u):
    # Call the page and return the result

    try:
        r = requests.get(u)

    except requests.ConnectionError:
        if settings.DEBUG:
            print("Problem connecting to FHIR Server")
        return HttpResponseRedirect(reverse_lazy('api:v1:home'))

    # test for errors:
    if r.status_code in [301, 302, 400, 403, 404, 500]:
        return error_status(r, r.status_code)

    j =json.loads(r.text, object_pairs_hook=OrderedDict)

    return j


def extract_info(item):
    # Extract the Patient Entry


    e = OrderedDict()

    this = item
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

    rand_str = ''.join(random.sample(string.ascii_lowercase, 6))

    print(rand_str)
    try:
        u = User.objects.get(username="u"+e['id'])
        if settings.DEBUG:
            print("Updating:", "u"+e['id'])
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
            rand_email = rand_str +".unknown@example.com"
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
        c.save()
        if settings.DEBUG:
            print("Updating Crosswalk:",c.user)

    except Crosswalk.DoesNotExist:
        c = Crosswalk.objects.create(user=u, fhir_url_id=e['id'])
        if settings.DEBUG:
            print("Creating Crosswalk:", c.user)

    return u.username+",p" + e['id']+","+u.email

