"""
bbofuser: apps.v1api.views
FILE: patients
Created: 8/16/15 11:21 PM


"""
from django.contrib import messages

__author__ = 'Mark Scrimshire:@ekivemark'

import json
import requests

from collections import OrderedDict
from xml.dom import minidom

from xml.etree import ElementTree as ET

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect,
                         HttpResponse,
                         JsonResponse, )
from django.utils.safestring import mark_safe

from django.shortcuts import render, render_to_response
from django.template import RequestContext

from ..models import Crosswalk

from apps.v1api.utils import (get_format,
                              etree_to_dict,
                              xml_str_to_json_str,
                              get_url_query_string,
                              concat_string,
                              build_params)

from fhir.utils import kickout_404

from bbapi.utils import FhirServerUrl


# @login_required
def get_patient(request, Access_Mode=None, *args, **kwargs):
    """
    Display Patient Profile
    :param request:
    :param Access_Mode = [None], Open
    :param args:
    :param kwargs:
    :return:

    """
    # Access_Mode = None = Do Crosswalk using Request.user
    # Access_Mode = OPEN = use kwargs['patient_id']
    if settings.DEBUG:
        print("Request.GET :", request.GET)
        print("Access_Mode :", Access_Mode)
        print("KWargs      :", kwargs)
        print("Args        :", args)

    if Access_Mode == "OPEN" and kwargs['patient_id']!="":
        # Lookup using patient_id for fhir_url_id

        key = kwargs['patient_id'].strip()
    else:
        # DONE: Setup Patient API so that ID is not required
        # DONE: Do CrossWalk Lookup to get Patient ID
        if settings.DEBUG:
            print("Request User Beneficiary(Patient):", request.user)
        try:
            xwalk = Crosswalk.objects.get(user=request.user.id)
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
            # return HttpResponseRedirect(reverse('api:v1:home'))

        key = xwalk.fhir_url_id.strip()

        if settings.DEBUG:
            print("Crosswalk   :", xwalk)
            print("GUID        :", xwalk.guid)
            print("FHIR        :", xwalk.fhir)
            print("FHIR URL ID :", key)

    # We will deal internally in JSON Format if caller does not choose
    # a format
    in_fmt = "json"

    # fhir_server_configuration = {"SERVER":"http://fhir-test.bbonfhir.com:8081",
    #                              "PATH":"",
    #                              "RELEASE":"/baseDstu2"}
    # FHIR_SERVER_CONF = fhir_server_configuration
    # FHIR_SERVER = FHIR_SERVER_CONF['SERVER'] + FHIR_SERVER_CONF['PATH']

    # Since this is BlueButton and we are dealing with Patient Records
    # We need to limit the id search to the specific beneficiary.
    # A BlueButton user should not be able to request a patient profile
    # that is not their own.
    # We do this via the CrossWalk. The xwalk.fhir_url_id is the patient
    # id as used in the url. eg. /Patient/23/
    # FHIR also allows an enquiry with ?_id=23. We need to detect that
    # and remove it from the parameters that are passed.
    # All other query parameters should be passed through to the
    # FHIR server.

    # Add URL Parameters to skip_parm to ignore or perform custom
    # processing with them. Use lower case values for matching.
    # DO NOT USE Uppercase
    skip_parm = ['_id', '_format']



    mask = True

    pass_to = FhirServerUrl()
    pass_to += "/Patient"
    pass_to += "/"
    pass_to = pass_to + key + "/"

    # We need to detect if a format was requested in the URL Parameters
    # ie. _format=json|xml
    # modify get_format to default to return nothing. ie. make no change
    # internal data handling will be JSON
    # _format will drive external display
    # if no _format setting  we will display in html (Current mode)
    # if valid _format string we will pass content through to display in
    # raw format

    get_fmt = get_format(request.GET)
    print("pass_to:", pass_to)
    pass_to = pass_to + build_params(request.GET, skip_parm)
    print("pass_to added to:", pass_to)

    mask_to = settings.DOMAIN

    # Set Context
    context = {'display':"Patient",
               'name': "Patient",
               'mask': mask,
               'key': key,
               'get_fmt': get_fmt,
               'in_fmt': in_fmt,
               # 'output' : "test output ",
               # 'args'   : args,
               # 'kwargs' : kwargs,
               # 'get'    : request.GET,
               'pass_to': pass_to,
               }

    if settings.DEBUG:
        print("Calling Requests with:", pass_to)
    try:
        r = requests.get(pass_to)

        context = process_page(request,r,context)

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
                return JsonResponse(context['import_text'], safe=False)

        else:

            if context['text'] == "No user readable content to display" or context['text']=="":

                result = json.loads(context['result'], object_pairs_hook=OrderedDict)
                print("Result::", result)
                context['text'] += "<br/> extracting information from returned record:<br/>"
                context['text'] += "<table>\n"
                if 'name' in result:
                    patient_name = result['name'][0]['given'][0]
                    patient_name += " "
                    patient_name += result['name'][0]['family'][0]
                    context['text'] += tr_build_item("Patient Name&nbsp;&nbsp;",
                                                     patient_name)
                if 'address' in result:
                    context['text'] += tr_build_item("Patient Address",
                                                     result['address'][0]['line'][0])
                if 'birthDate' in result:
                    context['text'] += tr_build_item("Birth Date", result['birthDate'])

                if 'identifier' in result:
                    context['text'] += tr_build_item("Patient ID",
                                                     result['identifier'][0]['value'])
                context['text'] += "</table>"

            return render_to_response('v1api/patient.html',
                                      RequestContext(request,
                                                     context, ))

    except requests.ConnectionError:
        print("Whoops - Problem connecting to FHIR Server")
        messages.error(request,
                       "FHIR Server is unreachable. Are you on the CMS Network?")
        return HttpResponseRedirect(reverse('api:v1:home'))


@login_required
def get_eob(request, Access_Mode=None, *args, **kwargs):
    """

    Display one or more EOBs but Always limit scope to Patient_Id

    :param request:
    :param eob_id:  Request a specific EOB
    :param args:
    :param kwargs:
    :return:
    """
    if settings.DEBUG:
        print("Request User Beneficiary(Patient):", request.user,
              "\nFor EOB Enquiry ")
        print("Request.GET :", request.GET)
        print("Access_Mode :", Access_Mode)
        print("KWargs      :", kwargs)
        print("Args        :", args)

    if Access_Mode == "OPEN" and kwargs['patient_id']!="":
        # Lookup using patient_id for fhir_url_id

        key = kwargs['patient_id'].strip()

    else:
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

        key = xwalk.fhir_url_id.strip()

    if settings.DEBUG:
        print("FHIR URL ID :", key)

    # We should have the xwalk.FHIR_url_id
    # So we will construct the EOB Identifier to include
    # This is a hack to limit EOBs returned to this user only.

    #   id_source['system'] = "https://mymedicare.gov/claims/beneficiary"
    #    id_source['use'] = "official"
    #    id_source['value'] = "Patient/"+str(patient_id)
    #    id_list.append(unique_id(id_source))

    # this search works:
    # http://fhir.bbonfhir.com:8080/fhir-p/
    # search?serverId=bbonfhir_dev
    # &resource=ExplanationOfBenefit
    # &param.0.0=https%3A%2F%2Fmymedicare.gov%2Fclaims%2Fbeneficiary
    # &param.0.1=Patient%2F4995401
    # &param.0.name=identifier
    # &param.0.type=token
    # &sort_by=
    # &sort_direction=
    # &resource-search-limit=

    # http://ec2-52-4-198-86.compute-1.amazonaws.com:8081/baseDstu2/
    # ExplanationOfBenefit/?patient=Patient/131052&_format=json

    #

    # We will deal internally in JSON Format if caller does not choose
    # a format
    in_fmt = "json"
    get_fmt = get_format(request.GET)

    # DONE: Define Transaction Dictionary to enable generic presentation of API Call
    Txn = {'name': "ExplanationOfBenefit",
           'display': 'EOB',
           'mask': True,
           'template': 'v1api/eob.html',
           'in_fmt': in_fmt,
           }

    skip_parm = ['_id', '_format', 'patient']

    mask = True

    pass_to = FhirServerUrl()
    pass_to += "/ExplanationOfBenefit"
    pass_to += "/"

    # We can allow an EOB but we MUST add a search Parameter
    # to limit the items found to those relevant to the Patient Id
    #if eob_id:
    #    pass_to = eob_id + "/"

    # Now apply the search restriction to limit to patient _id

    #pass_to = pass_to + key + "/"

    pass_to += "?patient="
    pass_to += "Patient/"
    pass_to += key

    pass_to = pass_to + "&" + build_params(request.GET, skip_parm)[1:]
    if settings.DEBUG:
        print("Pass_to from build_params:", pass_to)

    if settings.DEBUG:
        print("Calling requests with pass_to:", pass_to)

    # Set Context
    context = {'display': 'EOB',
               'name': 'ExplanationOfBenefit',
               'mask': mask,
               'key': key,
               'get_fmt': get_fmt,
               'in_fmt': in_fmt,
               'pass_to': pass_to,
               }

    try:
        r = requests.get(pass_to)

        context = process_page(request,r,context)

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
                return JsonResponse(context['import_text'], safe=False)

        else:

            if context['text'] == "No user readable content to display" or context['text']=="":

                result = json.loads(context['result'], object_pairs_hook=OrderedDict)
                print("Result::", result)
                context['text'] += "<br/> extracting information from returned record:<br/>"
                context['text'] += "<table>\n"
                if 'name' in result:
                    patient_name = result['name'][0]['given'][0]
                    patient_name += " "
                    patient_name += result['name'][0]['family'][0]
                    context['text'] += tr_build_item("Patient Name&nbsp;&nbsp;",
                                                     patient_name)
                if 'address' in result:
                    context['text'] += tr_build_item("Patient Address",
                                                     result['address'][0]['line'][0])
                if 'birthDate' in result:
                    context['text'] += tr_build_item("Birth Date", result['birthDate'])

                if 'identifier' in result:
                    context['text'] += tr_build_item("Patient ID",
                                                     result['identifier'][0]['value'])
                context['text'] += "</table>"


        return render_to_response('v1api/eob.html',
                                      RequestContext(request,
                                                     context, ))

    except requests.ConnectionError:
        print("Whoops - Problem connecting to FHIR Server")
        messages.error(request,
                       "FHIR Server is unreachable. "
                       "Are you on the CMS Network?")

    return HttpResponseRedirect(reverse('api:v1:home'))


#@login_required
def get_eob_view(request, eob_id, *args, **kwargs):
    """

    Display one or more EOBs but Always limit scope to Patient_Id

    :param request:
    :param eob_id:  Request a specific EOB
    :param args:
    :param kwargs:
    :return:
    """
    if settings.DEBUG:
        print("Request User Beneficiary(Patient):", request.user,
              "\nFor Single EOB")
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

    # DONE: Define Transaction Dictionary to enable generic presentation of API Call
    Txn = {'name': "ExplanationOfBenefit",
           'display': 'EOB',
           'mask': True,
           # 'server': settings.FHIR_SERVER,
           # 'locn': "/baseDstu2/ExplanationOfBenefit/",
           'template': 'v1api/eob.html',
           'in_fmt': in_fmt,
           }

    skip_parm = ['_id', '_format']

    key = xwalk.fhir_url_id.strip()

    mask = False
    if 'mask' in Txn:
        mask = Txn['mask']

    pass_to = FhirServerUrl()
    pass_to += "/ExplanationOfBenefit/"

    # We can allow an EOB but we MUST add a search Parameter
    # to limit the items found to those relevant to the Patient Id
    if eob_id:
        pass_to = pass_to + eob_id + "/"

    # Now apply the search restriction to limit to patient _id

    #pass_to = pass_to + key + "/"

    pass_to = pass_to + "?patient="
    pass_to = pass_to + "Patient/"
    pass_to = pass_to + xwalk.fhir_url_id.strip()

    pass_to = pass_to + "&" + build_params(request.GET, skip_parm)
    if settings.DEBUG:
        print("Pass_to from build_params:", pass_to)

    if settings.DEBUG:
        print("Calling requests with pass_to:", pass_to)

    # Set Context
    context = {'display': Txn['display'],
               'name': Txn['name'],
               'mask': mask,
               'key': key,
               'get_fmt': get_fmt,
               'in_fmt': Txn['in_fmt'],
               # 'output' : "test output ",
               # 'args'   : args,
               # 'kwargs' : kwargs,
               # 'get'    : request.GET,
               'pass_to': pass_to,
               }

    try:
        r = requests.get(pass_to)

        if get_fmt == "xml":
            xml_text = minidom.parseString(r.text)
            pretty_xml = xml_text.toprettyxml()
            context['result'] = pretty_xml  # convert
            context['text'] = pretty_xml

            return HttpResponse(context['result'],
                                content_type='application/' + get_fmt)

        else: # get_fmt == "json" or None:

            convert = OrderedDict(r.json())
            # result = mark_safe(convert)

            if settings.DEBUG:
                print("Convert:", convert)

            content = OrderedDict(convert)
            text = ""

            context['result'] = r.json()  # convert
            if 'text' in content:
                context['text'] = content['text']['div']
                if 'issue' in content:
                    context['error'] = content['issue']
            else:
                if settings.DEBUG:
                    print("Resource:", convert['entry'])
                context['text'] = convert['entry']

            if get_fmt == "json":
                return JsonResponse(context['result'], )

        return render_to_response(Txn['template'],
                                      RequestContext(request,
                                                     context, ))

    except requests.ConnectionError:
        print("Whoops - Problem connecting to FHIR Server")
        messages.error(request,
                       "FHIR Server is unreachable. "
                       "Are you on the CMS Network?")

    return HttpResponseRedirect(reverse('api:v1:home'))


def process_page(request, r, context):
    """
    Process the request

    :param request:
    :param r:
    :param context:
    :return: context
    """

    if context["get_fmt"] == "xml":

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

        if settings.DEBUG:
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
        context['import_text'] = import_text
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

    return context


def li_build_item(field_name, field_value):

    li_build_item = "<li>%s: %s</li>" % (field_name, field_value)

    return li_build_item


def tr_build_item(field_name, field_value):

    ti_build_item = "<tr>"
    ti_build_item += "<td>%s</td><td>%s</td>" % (field_name, field_value)
    ti_build_item += "</tr>"
    return ti_build_item