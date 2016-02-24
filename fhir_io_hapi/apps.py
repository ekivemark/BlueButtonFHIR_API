#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: apps.py
Created: 2/24/16 1:41 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.apps import AppConfig

class fhir_io_hapi_config(AppConfig):
    name = 'fhir_io_hapi'
    verbose_name = "fhir backend api interface"

    def ready(self):
        import fhir_io_hapi.signals
