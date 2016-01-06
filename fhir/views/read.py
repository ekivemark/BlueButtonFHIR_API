from django.shortcuts import render
from ..models import SupportedResourceType
from django.shortcuts import render
from collections import OrderedDict
from ..utils import kickout_404
from django.http import HttpResponse
import json

from xml.dom import minidom
from xml.etree.ElementTree import Element, tostring

from django.conf import settings
from fhir_data.views import get as fhir_db_get


def dict_to_xml(tag, d):
    '''
    Turn a simple dict of key/value pairs into XML
    '''
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)
    return elem


def read(request, resource_type, id):
    """Read FHIR Interaction"""
    # Example client use in curl:
    # curl  -X GET http://127.0.0.1:8000/fhir/Practitioner/1234
    
    try:
        rt = SupportedResourceType.objects.get(resource_name=resource_type)    
    except SupportedResourceType.DoesNotExist:
        msg = "%s is not a supported resource type on this FHIR server." % (resource_type)
        return kickout_404(msg)

    od = OrderedDict(fhir_db_get.read(request, resource_type, id))

    if settings.DEBUG:
        print("OD:", od)

    if od['format'] == "xml":
        if settings.DEBUG:
            print("We got xml back in od")
        return HttpResponse( tostring(dict_to_xml('content', od)), content_type="application/xml")
    else:

        return HttpResponse(json.dumps(od, indent=4),
                            content_type="application/json")

