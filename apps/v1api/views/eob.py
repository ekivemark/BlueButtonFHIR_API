#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: apps.v1api.views.eob
Created: 12/28/15 9:33 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

import json
import requests

from collections import OrderedDict

from xml.dom import minidom
from xml.etree import ElementTree as ET

from oauth2_provider.decorators import protected_resource
from oauth2_provider.models import AbstractApplication, AccessToken
from oauth2_provider.views.generic import ProtectedResourceView, View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import ListView

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import (reverse_lazy,
                                      reverse)
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpRequest,
                         JsonResponse)

from fhir.utils import kickout_404

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from apps.v1api.views.patient import get_patient
from apps.v1api.views.crosswalk import lookup_xwalk
from apps.v1api.utils import (build_params,
                              get_format,
                              concat_string)

from ..models import Crosswalk

from bbapi.utils import FhirServerUrl


class EOB(ListView):
    if settings.DEBUG:
        print("in apps.v1api.views.eob")

    def get(self, request, eob_id, *args, **kwargs):
        # This is an ExplanationOfBenefit profile GET
        #
        # use request.user to lookup a crosswalk
        # get the FHIR Patient ID
        # Call the FHIR Patient Profile
        # Return the result
        # EOB will need to look up request.user and apply a filter on the EOB
        # The filter in search Parameters will be the GUID
        # We need to load the GUID when we are loading EOBs and
        # Patient Records.

        # http://ec2-52-4-198-86.compute-1.amazonaws.com:8081/baseDstu2/
        # ExplanationOfBenefit/?patient=Patient/131052&_format=json

        if settings.DEBUG:
            print("in EOB.get with", eob_id)

        xwalk_id = lookup_xwalk(request, )
        if settings.DEBUG:
            print("crosswalk:", xwalk_id)

        if xwalk_id == None:
            return HttpResponseRedirect(reverse_lazy('api:v1:home'))

        if settings.DEBUG:
            print("now we need to evaluate the parameters and arguments"
                  " to work with ", xwalk_id, "and ", request.user)
            print("GET Parameters:", request.GET, ":")

        if patient_id == xwalk_id:
            key = eob_id
        else:
            key = xwalk_id.strip()

        in_fmt = "json"
        Txn = {'name': "ExplanationOfBenefit",
           'display': 'ExplanationOfBenefit',
           'mask': True,
           'server': settings.FHIR_SERVER,
           'locn': "/baseDstu2/ExplanationOfBenefit/",
           'template': 'v1api/eob.html',
           'in_fmt': in_fmt,
           }

        skip_parm = ['_id']
        pass_params = build_params(request.GET, skip_parm)

        if settings.DEBUG:
            print("Pass_params=", pass_params)

        pass_to = Txn['server'] + Txn['locn'] + key + "/"

        print("Here is the URL to send, %s now get parameters" % pass_to)

        if pass_params != "":
            pass_to = pass_to + pass_params

        try:
            r = requests.get(pass_to)

        except requests.ConnectionError:
            if settings.DEBUG:
                print("Problem connecting to FHIR Server")
            messages.error(request, "FHIR Server is unreachable." )
            return HttpResponseRedirect(reverse_lazy('api:v1:home'))

        text_out = ""
        if '_format=xml' in pass_to:
            text_out= minidom.parseString(r.text).toprettyxml()
        else:
            text_out = r.json()

        return HttpResponse('This is the EOB Pass Thru %s using %s '
                            'and with response of %s' % (xwalk_id,
                                                         pass_to,
                                                         text_out))


#@csrf_exempt
#@login_required
#@protected_resource(scopes=['read write_consent'])
def ExplanationOfBenefit(request, *args, **kwargs):
    """
    Function-based interface to ExplanationOfBenefit
    :param request:
    :return:
    """

    if settings.DEBUG:
        print("In apps.v1api.views.eob.ExplanationOfBenefit Function")

        print("request:", request.GET)

    process_mode = request.META['REQUEST_METHOD']

    try:
        xwalk = Crosswalk.objects.get(user=request.user)
    except Crosswalk.DoesNotExist:
        messages.error(request, "Unable to find Patient ID")
        return HttpResponseRedirect(reverse('api:v1:home'))

    if xwalk.fhir_url_id == "":
        err_msg = ['Sorry, We were unable to find',
                   'your record', ]
        exit_message = concat_string("",
                                     msg=err_msg,
                                     delimiter=" ",
                                     last=".")
        messages.error(request, exit_message)
        return HttpResponseRedirect(reverse('api:v1:home'))

    in_fmt = "json"
    get_fmt = get_format(request.GET)

    Txn = {'name': "ExplanationOfBenefit",
           'display': 'EOB',
           'mask': True,
           'template': 'v1api/eob.html',
           'in_fmt': in_fmt,
           }

    if settings.DEBUG:
        print("Request.GET :", request.GET)
        print("KWargs      :", kwargs)
        print("Crosswalk   :", xwalk)
        print("GUID        :", xwalk.guid)
        print("FHIR        :", xwalk.fhir)
        print("FHIR URL ID :", xwalk.fhir_url_id)

    # We should have the xwalk.FHIR_url_id
    # So we will construct the EOB Identifier to include

    # We will deal internally in JSON Format if caller does not choose
    # a format
    in_fmt = "json"
    get_fmt = get_format(request.GET)

    pass_to = FhirServerUrl()
    pass_to += "/ExplanationOfBenefit/"

    key = xwalk.fhir_url_id.strip()
    patient_filter= "?patient=Patient/" + key

    pass_to += patient_filter

    skip_parm = ['_id', '_format']

    pass_to = pass_to + "&" + build_params(request.GET, skip_parm)[1:]

    # Set Context
    context = {'display':"EOB",
               'name': "ExplanationOfBenefit",
               'mask': True,
               'key': key,
               'get_fmt': get_fmt,
               'in_fmt': in_fmt,
               'pass_to': pass_to,
               }

    if settings.DEBUG:
        print("Calling requests with pass_to:", pass_to)

    try:
        r = requests.get(pass_to)

        if get_fmt == "xml":

            xml_text = minidom.parseString(r.text)
            print("XML_TEXT:", xml_text.toxml())
            root = ET.fromstring(r.text)
            # root_out = etree_to_dict(r.text)

            json_string = ""
            # json_out = xml_str_to_json_str(r.text, json_string)
            if settings.DEBUG:
                print("Root ET XML:", root)
                # print("XML:", root_out)
                # print("JSON_OUT:", json_out,":", json_string)

            drill_down = ['Bundle',
                          'entry',
                          'Patient', ]
            level = 0

            tag0 = xml_text.getElementsByTagName("text")
            # tag1 = tag0.getElementsByTagName("entry")

            print("Patient?:", tag0)
            print("DrillDown:", drill_down[level])
            print("root find:", root.find(drill_down[level]))

            pretty_xml = xml_text.toprettyxml()
            #if settings.DEBUG:
            #    print("TEXT:", text)
            #    # print("Pretty XML:", pretty_xml)

            context['result'] = pretty_xml  # convert
            context['text'] = pretty_xml

        else:

            convert = OrderedDict(r.json())
            # result = mark_safe(convert)

            if settings.DEBUG:
                print("Convert:", convert)
                # print("Next Level - entry:", convert['entry'])
                # print("\n ANOTHER Level- text:", convert['entry'][0])

            content = OrderedDict(convert)
            text = ""

            if settings.DEBUG:
                print("Content:", content)
                print("resourceType:", content['resourceType'])
                if 'text' in content:
                    if 'div' in content['text']:
                        print("text:", content['text']['div'])

            # context['result'] = r.json()  # convert
            import_text = json.loads(r.text, object_pairs_hook=OrderedDict)
            context['result'] = json.dumps(import_text, indent=4, sort_keys=False)
            if 'text' in content:
                if 'div' in content['text']:
                    context['text'] = content['text']['div']
                else:
                    context['text'] = ""
            else:
                context['text'] = "No user readable content to display"
            if 'error' in content:
                context['error'] = context['issue']

        # Setup the page

        if settings.DEBUG:
            print("Context-result:", context['result'])
            # print("Context-converted:", json.dumps(context['result'], sort_keys=False))
            # print("Context:",context)

        if get_fmt == 'xml' or get_fmt == 'json':
            if settings.DEBUG:
                print("Mode = ", get_fmt)
                print("Context['result']: ", context['result'])
            if get_fmt == "xml":
                return HttpResponse(context['result'],
                                    content_type='application/' + get_fmt)
            if get_fmt == "json":
                #return HttpResponse(context['result'], mimetype="application/json")
                return JsonResponse(import_text, safe=False  )

        else:
            return render_to_response(Txn['template'],
                                      RequestContext(request,
                                                     context, ))

    except requests.ConnectionError:
        print("Whoops - Problem connecting to FHIR Server")
        messages.error(request,
                       "FHIR Server is unreachable. Are you on the CMS Network?")
        return HttpResponseRedirect(reverse('api:v1:home'))


def PatientExplanationOfBenefit(request, patient_id=None, *args, **kwargs):
    """
    Function-based interface to ExplanationOfBenefit
    :param request:
    :return:
    """

    if patient_id == None:
        try:
            xwalk = Crosswalk.objects.get(user=request.user.id)

            patient_id = xwalk.fhir_url_id

        except Crosswalk.DoesNotExist:
            reason = "Unable to find Patient ID for user:%s[%s]" % (request.user,
                                                                request.user.id)
            messages.error(request, reason)
            return kickout_404(reason)
            # return HttpResponseRedirect(reverse('api:v1:home'))

        if xwalk.fhir_url_id == "":
            err_msg = ['Crosswalk lookup failed: Sorry, We were unable to find',
                       'your record', ]
            exit_message = concat_string("",
                                         msg=err_msg,
                                         delimiter=" ",
                                         last=".")
            messages.error(request, exit_message)
            return kickout_404(exit_message)

    if patient_id == "":
        err_msg = ['Sorry, No Patient Id provided', ]
        exit_message = concat_string("",
                                     msg=err_msg,
                                     delimiter=" ",
                                     last=".")
        messages.error(request, exit_message)
        return HttpResponseRedirect(reverse('api:v1:home'))

    if settings.DEBUG:
        print("In apps.v1api.views.eob.PatientExplanationOfBenefit Function")

        print("request:", request.GET)

    process_mode = request.META['REQUEST_METHOD']

    in_fmt = "json"
    get_fmt = get_format(request.GET)

    Txn = {'name': "ExplanationOfBenefit",
           'display': 'EOB',
           'mask': True,
           'template': 'v1api/eob.html',
           'in_fmt': in_fmt,
           }

    if settings.DEBUG:
        print("Request.GET :", request.GET)
        print("KWargs      :", kwargs)
        print("Patient     :", patient_id)

    # We should have the xwalk.FHIR_url_id
    # So we will construct the EOB Identifier to include

    # We will deal internally in JSON Format if caller does not choose
    # a format
    in_fmt = "json"
    get_fmt = get_format(request.GET)

    pass_to = FhirServerUrl()
    pass_to += "/ExplanationOfBenefit/"

    key = patient_id
    patient_filter= "?patient=Patient/" + key

    pass_to += patient_filter

    skip_parm = ['_id', '_format']

    pass_to = pass_to + "&" + build_params(request.GET, skip_parm)[1:]

    # Set Context
    context = {'display':"EOB",
               'name': "ExplanationOfBenefit",
               'mask': True,
               'key': key,
               'get_fmt': get_fmt,
               'in_fmt': in_fmt,
               'pass_to': pass_to,
               }

    if settings.DEBUG:
        print("Calling requests with pass_to:", pass_to)

    try:
        r = requests.get(pass_to)

        if get_fmt == "xml":

            xml_text = minidom.parseString(r.text)
            print("XML_TEXT:", xml_text.toxml())
            root = ET.fromstring(r.text)
            # root_out = etree_to_dict(r.text)

            json_string = ""
            # json_out = xml_str_to_json_str(r.text, json_string)
            if settings.DEBUG:
                print("Root ET XML:", root)
                # print("XML:", root_out)
                # print("JSON_OUT:", json_out,":", json_string)

            drill_down = ['Bundle',
                          'entry',
                          'Patient', ]
            level = 0

            tag0 = xml_text.getElementsByTagName("text")
            # tag1 = tag0.getElementsByTagName("entry")

            print("Patient?:", tag0)
            print("DrillDown:", drill_down[level])
            print("root find:", root.find(drill_down[level]))

            pretty_xml = xml_text.toprettyxml()
            #if settings.DEBUG:
            #    print("TEXT:", text)
            #    # print("Pretty XML:", pretty_xml)

            context['result'] = pretty_xml  # convert
            context['text'] = pretty_xml

        else:

            convert = OrderedDict(r.json())
            # result = mark_safe(convert)

            if settings.DEBUG:
                print("Convert:", convert)
                # print("Next Level - entry:", convert['entry'])
                # print("\n ANOTHER Level- text:", convert['entry'][0])

            content = OrderedDict(convert)
            text = ""

            if settings.DEBUG:
                print("Content:", content)
                print("resourceType:", content['resourceType'])
                if 'text' in content:
                    if 'div' in content['text']:
                        print("text:", content['text']['div'])

            # context['result'] = r.json()  # convert
            import_text = json.loads(r.text, object_pairs_hook=OrderedDict)
            context['result'] = json.dumps(import_text, indent=4, sort_keys=False)
            if 'text' in content:
                if 'div' in content['text']:
                    context['text'] = content['text']['div']
                else:
                    context['text'] = ""
            else:
                context['text'] = "No user readable content to display"
            if 'error' in content:
                context['error'] = context['issue']

        # Setup the page

        if settings.DEBUG:
            print("Context-result:", context['result'])
            # print("Context-converted:", json.dumps(context['result'], sort_keys=False))
            # print("Context:",context)

        if get_fmt == 'xml' or get_fmt == 'json':
            if settings.DEBUG:
                print("Mode = ", get_fmt)
                print("Context['result']: ", context['result'])
            if get_fmt == "xml":
                return HttpResponse(context['result'],
                                    content_type='application/' + get_fmt)
            if get_fmt == "json":
                #return HttpResponse(context['result'], mimetype="application/json")
                return JsonResponse(import_text, safe=False  )

        else:
            return render_to_response(Txn['template'],
                                      RequestContext(request,
                                                     context, ))

    except requests.ConnectionError:
        print("Whoops - Problem connecting to FHIR Server")
        messages.error(request,
                       "FHIR Server is unreachable. Are you on the CMS Network?")
        return HttpResponseRedirect(reverse('api:v1:home'))
