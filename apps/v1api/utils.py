"""
bbofuser
FILE: utils
Created: 8/17/15 11:44 AM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

import json
import time

from lxml import etree

from collections import (OrderedDict,
                         defaultdict)
from datetime import datetime

from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string

FORMAT_OPTIONS = ['json', 'xml']


def get_to_lower(in_get):
    """
    Force the GET parameter keys to lower case
    :param in_get:
    :return:
    """

    if not in_get:
        if settings.DEBUG:
            print("get_to_lower: Nothing to process")
        return in_get

    got_get = OrderedDict()
    # Deal with capitalization in request.GET.
    # force to lower
    for value in in_get:

        got_get[value.lower()] = in_get.get(value,"")
        if settings.DEBUG:
            print("Got key", value.lower(), ":", got_get[value.lower()] )

    if settings.DEBUG:
        print("Returning lowercase request.GET", got_get)

    return got_get


def get_format(in_get):
    """
    Receive request.GET and check for _format
    if json or xml return .lower()
    if none return "json"
    :param in_get:
    :return: "json" or "xml"
    """
    got_get = get_to_lower(in_get)

    # set default to return
    result = ""

    if "_format" in got_get:
        # we have something to process

        if settings.DEBUG:
            print("In Get:",in_get)
        fmt = got_get.get('_format','').lower()

        if settings.DEBUG:
            print("Format Returned:", fmt)

        # Check for a valid lower case value
        if fmt in FORMAT_OPTIONS:
            result = fmt
        else:
            if settings.DEBUG:
                print("No Match with Format Options:", fmt)

    return result


def xml_str_to_json_str(xmls_input, jsons_output):
    """
    Converts an xml string to json.
    """
    json_return = dict_to_json_str(etree_to_dict(xmls_to_etree(xmls_input),
                                                 True),
                                   jsons_output)
    return json_return

def xml_to_json(xml_input, json_output):
    """
    Converts an xml file to json.
    """
    dict_to_json(etree_to_dict(xml_to_etree(xml_input),
                               True),
                 json_output)
    return

def dict_to_json_str(dictionary, jsons_output):
    """
    Converts a dictionary to a json string
    :param dictionary:
    :param jsons_output:
    :return:
    """
    jsons_output = json.dumps(dictionary,
                              sort_keys=True,
                              indent=4)
    return jsons_output

def xmls_to_etree(xml_input):
    """Converts xml to a lxml etree."""
    return etree.HTML(xml_input)

def xml_to_etree(xml_input):
    """Converts xml to a lxml etree."""
    f = open(xml_input, 'r')
    xml = f.read()
    f.close()
    return etree.HTML(xml)

def etree_to_dict(tree, only_child):
    """Converts an lxml etree into a dictionary."""

    mydict = dict([(item[0], item[1]) for item in tree.items()])
    children = tree.getchildren()
    if children:
        if len(children) > 1:
            mydict['children'] = [etree_to_dict(child,
                                                False) for child in children]
        else:
            child = children[0]
            mydict[child.tag] = etree_to_dict(child,
                                              True)
    if only_child:
        return mydict
    else:
        return {tree.tag: mydict}

def dict_to_json(dictionary, json_output):
    """
    Converts a dictionary into a json file.
    :param dictionary:
    :param json_output:
    :return:
    """
    f = open(json_output,
             'w')
    f.write(json.dumps(dictionary,
                       sort_keys=True,
                       indent=4))
    f.close()
    return

def build_fhir_profile(request,context={},
                       template="",
                       extn="json.html",
                       ):
    """
    Build a FHIR Profile in JSON
    Use to submit to FHIR Server
    :param template:
    :param extn: json.html or json.xml (use .html to enable
                    template editing error checking
            (this becomes the file extension for the template)
            sms is a brief template suitable for SMS Text Messages
    :param email:
    :return:
    """
    # Template files use the Django Template System.

    this_context = {}
    if context is not None:
        # print("BMT:Context is:", context)
        this_context = RequestContext(request, context)
        # print("BMT:this_context with context:", this_context)

    if request is not None:
        # print("BMT:Request is:", request)
        this_context = RequestContext(request, this_context)

    if template=="":
        template="v1api/fhir_profile/practitioner"

    source_plate = template + "." + extn

    profile = render_to_string(source_plate, this_context)
    #if settings.DEBUG:
    #    print("Profile:",profile)

    return profile


def date_to_iso(thedate, decimals=True):
    """
    Convert date to isoformat time
    :param thedate:
    :return:
    """

    strdate = thedate.strftime("%Y-%m-%dT%H:%M:%S")

    minute = (time.localtime().tm_gmtoff / 60) % 60
    hour = ((time.localtime().tm_gmtoff / 60) - minute) / 60
    utcoffset = "%.2d%.2d" %(hour, minute)

    if decimals:
        three_digits = "."+ str(thedate.microsecond)[:3]
    else:
        three_digits = ""

    if utcoffset[0] != '-':
        utcoffset = '+' + utcoffset

    return strdate + three_digits + utcoffset

def get_url_query_string(get, skip_parm=[]):
    """
    Receive the request.GET Query Dict
    Evaluate against skip_parm by skipping any entries in skip_parm
    Return a query string ready to pass to a REST API.
    http://hl7-fhir.github.io/search.html#all

    # We need to force the key to lower case and skip params should be
    # lower case too

    eg. _lastUpdated=>2010-10-01&_tag=http://acme.org/codes|needs-review

    :param get: {}
    :param skip_parm: []
    :return: Query_String (QS)
    """

    # Check we got a get dict
    if not get:
        return ""

    qs = ""
    # Now we work through the parameters

    for k, v in get.items():
        if settings.DEBUG:
            print("K/V: [",k, "/", v,"]" )
        if k.lower() in skip_parm:
            pass
        else:
            # Build the query_string
            if len(qs) > 1:
                # Use & to concatanate items
                qs = qs + "&"
            # build the string
            qs = qs + k.strip() + "=" + v.strip()

    return qs

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


def build_params(get, skip_parm=['_id','_format']):
    """
    Build the URL Parameters.
    We have to skip any in the skip list.

    :param get:
    :return:
    """
    # We will default to json for content handling
    in_fmt = "json"

    pass_to = ""

    url_param = get_url_query_string(get, skip_parm)

    if "_format" in skip_parm:
        print("skip_parm dropped _format - url_param now:", url_param)

        # Check for _format and process in this section
        get_fmt = get_format(get)
        if settings.DEBUG:
            print("get_Format returned:", get_fmt)

        #get_fmt_type = "?_format=xml"
        #get_fmt_type = "?_format=json"

        if get_fmt:
            get_fmt_type = "_format=" + get_fmt

            pass_to = "?" + get_fmt_type
        else:
            if settings.DEBUG:
                print("Get Format:[", get_fmt, "]")
            in_fmt_type = "_format=" + in_fmt
            pass_to = "?" + in_fmt_type

    if len(url_param) > 1:
        if settings.DEBUG:
            print("URL Params = ", url_param)
        if "?" in pass_to:
            # We already have the start of a query string in the url
            # So we prefix with "&"
            pass_to = pass_to + "&" + url_param
        else:
            # There is no ? so we need to start the query string
            pass_to = pass_to + "?" + url_param
    if settings.DEBUG:
        print("URL Pass_To:", pass_to)

    return pass_to