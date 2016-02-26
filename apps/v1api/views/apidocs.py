#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: apidocs
Created: 2/25/16 6:13 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.views.generic import ListView

from fhir.models import SupportedResourceType
from fhir_io_hapi.models import ResourceTypeControl

class ResourceTypeList(ListView):
    model = SupportedResourceType


class ResourceControlList(ListView):
    model = ResourceTypeControl

