import json

from collections import OrderedDict

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from fhir.models import SupportedResourceType
from fhir.settings import FHIR_BACKEND, DF_EXTRA_INFO
from fhir.utils import (kickout_404, kickout_403)
from fhir.views.utils import check_access_interaction_and_resource_type

from django.conf import settings


def read(request, resource_type, id):
    """Read FHIR Interaction"""
    # Example client use in curl:
    # curl  -X GET http://127.0.0.1:8000/fhir/Practitioner/1234
    
    interaction_type = 'read'
    #Check if this interaction type and resource type combo is allowed.
    deny = check_access_interaction_and_resource_type(resource_type, interaction_type)
    if deny:
        #If not allowed, return a 4xx error.
        return deny

    #testing direct response
    return FHIR_BACKEND.read(request, resource_type, id)

    # move to fhir_io_mongo (pluggable backend)

    od = OrderedDict()
    if DF_EXTRA_INFO:
        od['request_method']= request.method
        od['interaction_type'] = interaction_type
    od['resource_type']    = resource_type
    od['id'] = id
    if DF_EXTRA_INFO:
        od['note'] = "This is only a stub for future implementation"
    return HttpResponse(json.dumps(od, indent=4),
                        content_type="application/json")
