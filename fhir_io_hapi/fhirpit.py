#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: fhirpit
Created: 1/28/16 10:05 PM

Construct a fhir url

"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.conf import settings

from apps.v1api.models import Crosswalk

SEPARATOR = "/"

QMARK = "?"

FHIR_SERVER_CONF = {
        'SERVER': "http://fhir.bbonfhir.com",
        'PATH': "/fhir-p",
        'RELEASE': "/baseDstu2",
        }

# Build the Server and Path specification
# FHIR_SERVER = 'http://fhir.bbonfhir.com/fhir-p'
# FHIR_SERVER = 'http://localhost:8080/fhir-p'
FHIR_SERVER = FHIR_SERVER_CONF['SERVER']+FHIR_SERVER_CONF['PATH'] + FHIR_SERVER_CONF['RELEASE']

def build_url(Resource="", Id=""):
    """
    Construct the URL from fixed settings and variable parameters
    :param Resource:
    :param Id:
    :return:
    """

    Server = FHIR_SERVER + SEPARATOR + Resource
    if Resource == "":
        pass
    else:
        if Id == "":
            pass

        else:
            Server += SEPARATOR + Id

    if settings.DEBUG:
        print("URL:", Server )

    return Server


def mask_id(user, id, Resource=""):
    """
    Mask the ID field if it relates to a Beneficiary.

    We replace the submitted Id value with the actual URL Id assigned to the resource.
    This is done to prevent a request being made via one beneficiary account to retrieve the
    record of another beneficiary.

    :param id:
    :param Resource:
    :return:
    """

    if Resource.lower() == "patient":
        # Lookup in the crosswalk to replace id
        try:
            bene = Crosswalk.objects.get(user=user)
            if bene.fhir_url_id == "":
                return id
            else:
                return bene.fhir_url_id

        except Crosswalk.DoesNotExist:
            return id

