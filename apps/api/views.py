"""
bbofuser:api
FILE: views
Created: 8/3/15 6:54 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.conf import settings
from django.shortcuts import (render,
                              render_to_response)
from django.template import RequestContext

# DONE: Login_Required Decorator for Device Accounts
# DONE: Allow versioning of api (v1)
# DONE: Create API Landing Page (Unauthenticated)

def api_index(request):
    # Show API Home Page

    DEBUG = settings.DEBUG_SETTINGS

    if DEBUG:
        print(settings.APPLICATION_TITLE, "in apps.api.views.api_index")

    context = {}
    return render_to_response('api/index.html',
                              RequestContext(request, context, ))

