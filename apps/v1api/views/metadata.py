#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: metadata
Created: 4/2/16 10:11 AM


"""

import json
import requests

from collections import OrderedDict

from django.conf import settings

from django.http import HttpResponse

from fhir.models import SupportedResourceType

from ..utils import (FhirServerUrl,
                     re_write_url,
                     re_write_to)

__author__ = 'Mark Scrimshire:@ekivemark'

def fhir_metadata(request):
    """"
    fhir conformance statement

    """

    # prototype output

    conform = OrderedDict()
    pass_to = FhirServerUrl() + "/metadata"

    r = requests.get(pass_to)


    conform['resourceType'] = "Conformance"
    conform['url'] = settings.URL_PRE + settings.DOMAIN + request.get_full_path().rstrip(
        '/metadata')
    conform['version'] = settings.VERSION_INFO
    conform['format'] = ["json", "xml"]
    conform['name'] = "CMS Blue Button on FHIR Data API"
    conform['status'] = "draft"
    conform['experimental'] = True
    conform['Publisher'] = "Centers for Medicare and Medicaid Services, " \
                           "Office of Enterprise Data Analytics"

    conform['fhirVersion'] = "2.11"

    od = OrderedDict()
    od = re_write_to(r.text)

    od['rest'] = filter_resourceType(od['rest'])

    conform = re_write_to(r.text)

    conform['rest'] = od['rest']

    conform['implementation'] = {"description": "BBonFIR_API:Experimental API "
                                                "with synthetic data. backend HAPI FHIR Server support.",
                                 "url": "/api/v1"},

    return HttpResponse(json.dumps(conform, indent=4),
                        content_type="application/json")


def filter_resourceType(rest):
    """
    filter the rest list and drop anything except SupportedResourceTypes

    {
     rest[
          {
           resource[
                    {type:string}
                   ]
           },
          ],
    }
    """

    od = OrderedDict()

    ct = 0
    for rest_item in rest:

        # print("%s item(s) in rest" % ct)
        # print("This is a %s" % (type(rest)))
        # print("contained item is a %s" % (type(rest_item)))

        if 'resource' in rest_item:
            r_ct = 0
            re_write_resource = False
            for resource_item, value in rest_item.items():
                # print("Resource item[%s]:%s" % (r_ct, resource_item))

                if resource_item == "resource":
                    # print("Resource Count: %s" % len(value))
                    active_resourceTypes = []
                    rd_ct = 0
                    for resource_dict in value:
                        resource_name = resource_dict['type']
                        # print("Processing:", resource_name)
                        for resource_dict_item, resource_dict_value in resource_dict.items():
                            if resource_dict_item == "type":
                                try:
                                    # print("Checking %s" % (resource_dict_item))
                                    r = SupportedResourceType.objects.get(resource_name=resource_dict_value)
                                    active_resourceTypes.append(resource_dict)
                                    # print("Found:", resource_dict_value)
                                except SupportedResourceType.DoesNotExist:
                                    re_write_resource = True
                                    # print("NOT Found:", resource_dict_value)
                            if resource_dict_item == 'interaction':
                                interaction_value = interaction_filter(resource_dict_value, resource_name)
                                resource_dict[resource_dict_item] = interaction_value
                                # print("Was ", resource_dict_value)
                                # print("Now ", interaction_value)

                        rd_ct += 1
                    if re_write_resource:
                        # print("Active Resources: %s" % len(active_resourceTypes))
                        # print(active_resourceTypes)
                        # print("r_ct = ", r_ct, ":", resource_item, ":", resource_dict)
                        # print("rewriting rest[%s][%s]" % (ct, rd_ct))

                        rest[ct] = active_resourceTypes

                r_ct += 1
        ct += 1
    # print("Rest is now:")
    # print(rest)

    return rest


def interaction_filter(interaction, resource_name):
    """
    check which interactions are allowed
    """
    od = []
    try:
        rt = SupportedResourceType.objects.get(resource_name=resource_name)
        for item in interaction:
            if item['code'] == 'read' and rt.read:
                od.append(item)
            if item['code'] ==  'vread' and rt.vread:
                od.append(item)
            if item['code'] == 'update' and rt.update:
                od.append(item)
            if item['code'] == 'delete' and rt.delete:
                od.append(item)
            if 'history' in item['code'] and rt.history:
                od.append(item)
            if item['code'] == 'create' and rt.create:
                od.append(item)
            if 'search' in item['code'] and rt.search:
                od.append(item)
        # print("Interactions:", od)
        return od
    except SupportedResourceType.DoesNotExist:
        return []



