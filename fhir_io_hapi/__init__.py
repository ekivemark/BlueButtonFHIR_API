#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
django-fhir
FILE: __init__.py
Created: 1/6/16 5:07 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'


# Hello World is here to test the loading of the module from fhir.settings
# from .settings import *
#from fhir_io_hapi.views.get import hello_world

#from fhir_io_hapi.views.delete import delete

#from fhir_io_hapi.views.get import (read, vread, history)

#from fhir_io_hapi.views.search import find

# Used to load post_save signal for write to backend fhir server
default_app_config = 'fhir_io_hapi.apps.fhir_io_hapi_config'

