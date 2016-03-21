from django.conf import settings
from django.shortcuts import render

from fhir.models import SupportedResourceType

from collections import OrderedDict

from django.http import HttpResponse
from importlib import import_module
import json

from fhir.utils import kickout_400, DEBUG_EXTRA_INFO
from fhir.views.utils import check_access_interaction_and_resource_type
from fhir.settings import FHIR_BACKEND_FIND



def search(request, resource_type):
    interaction_type = 'search'
    #Check if this interaction type and resource type combo is allowed.
    deny = check_access_interaction_and_resource_type(resource_type, interaction_type)
    if deny:
        #If not allowed, return a 4xx error.
        return deny

    """Search Interaction"""
    # Example client use in curl:
    # curl -X GET  http://127.0.0.1:8000/fhir/Practitioner?foo=bar
    if request.method != 'GET':
        msg = "HTTP method %s not supported at this URL." % (request.method)
        return kickout_400(msg)

    if settings.DEBUG:
        print("FHIR_BACKEND in search:",FHIR_BACKEND_FIND )
    return FHIR_BACKEND_FIND.find(request, resource_type)


    # Move to fhir_io_mongo (Plugable back-end)
    od = OrderedDict()
    if DEBUG_EXTRA_INFO:
        od['request_method']= request.method
        od['interaction_type'] = "search"
    od['resource_type']    = resource_type
    od['search_params'] = request.GET
    od['note'] = "This is only a stub for future implementation"
    
    return HttpResponse(json.dumps(od, indent=4),
                        content_type="application/json")
