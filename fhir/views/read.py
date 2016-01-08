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


def read(request, resource_type, id):
    """Read FHIR Interaction"""
    # Example client use in curl:
    # curl  -X GET http://127.0.0.1:8000/fhir/Practitioner/1234
    
    try:
        rt = SupportedResourceType.objects.get(resource_name=resource_type)    
    except SupportedResourceType.DoesNotExist:
        msg = "%s is not a supported resource type on this FHIR server." % (resource_type)
        return kickout_404(msg)

    #testing direct response
    return fhir_db_get.read(request, resource_type, id)

