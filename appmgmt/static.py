#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: static
Created: 1/27/16 10:35 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

REDIRECT_URI = 'http://localhost:8002/appmanagement/poet_callback/'

POET_BUNDLE_INFO = {
    'TEST': {'bundle_ref': "T001",
             'endpoint': "http://localhost:8000/appmanagement/trust_test/",
             'token_url': "http://localhost:8000/o/token/",
             'client_id': "1234567890",
             'token': 'x12345678'},
    'POET': {'bundle_ref': "bluebutton_developer",
             'endpoint': "http://localhost:8002/api/entitycheck/",
             'token_url': "http://localhost:8002/o/token/",
             'authorize_url': "http://localhost:8002/o/authorize",
             'client_id': "cmsFHIRclientid",
             'client_secret': "cmsFHIRclientsecret",
             'token': 'cms_token_access'},
    'NATE': {'bundle_ref': "N001",
             'endpoint': "https://api.nate.org/trust_test/",
             'token_url': "http://api.nate.org/o/token/",
             'client_id': "1234567890",
             'token': 'x12345678'},
    'DIRECTTRUST': {'bundle_ref': "DT001",
             'endpoint': "https://api.directtrust.org/trust_test/",
             'token_url': "http://api.directtrust.org/o/token/",
             'client_id': "9876543210",
             'token': 'x87654321'}
}
