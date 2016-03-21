#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

from fhir.views.create import create
from fhir.views.rud import read_or_update_or_delete
from fhir.views.search import search
from fhir.views.history import history, vread
from fhir.views.hello import hello
from fhir.views.oauth import oauth_create, oauth_update

from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    
    #Hello

    url(r'hello', hello,
        name='fhir_hello'),

    # oAuth2 URLs
    # These are for create and update only for now.
        
    #update
    url(r'oauth2/(?P<resource_type>[^/]+)/(?P<id>[^/]+)',
        oauth_update,
        name='fhir_oauth_update'),
    
    #create ------------------------------
    url(r'oauth2/(?P<resource_type>[^/]+)', oauth_create,
        name='fhir_oauth_create'),
    
    
    #URLs with no authentication
    #Interactions on Resources
    #Vread GET --------------------------------
    url(r'(?P<resource_type>[^/]+)/(?P<id>[^/]+)/_history/(?P<vid>[^/]+)', vread,
        name='fhir_vread'),

    #History GET ------------------------------
    url(r'(?P<resource_type>[^/]+)/(?P<id>[^/]+)/_history', history,
        name='fhir_history'),
    
    # ---------------------------------------
    # Read GET
    # Update PUT
    # Delete DELETE
    # ---------------------------------------
    url(r'(?P<resource_type>[^/]+)/(?P<id>[^/]+)',
        read_or_update_or_delete,
        name='fhir_read_or_update_or_delete'),


    #Create  POST ------------------------------
    url(r'(?P<resource_type>[^/]+)', create,
        name='fhir_create'),
    
    
    #Search  GET ------------------------------
    url(r'(?P<resource_type>[^/]+)?', search,
        name='fhir_search'),

    ]
