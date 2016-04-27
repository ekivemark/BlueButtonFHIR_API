#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: accounts.views.myapps
Created: 4/26/16 4:23 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from oauth2_provider.models import Grant

from django.shortcuts import (HttpResponseRedirect, render)
from django.template import RequestContext

@login_required
def myapps(request):
    """ User's Application Dashboard

    List Apps with permission expiry date
    App management Options:
    1. Remove App
    2. Extend permission

    Models Required:

    - bbApplication
    - grant

    """

    try:
        granted = Grant.objects.filter(user=request.user)
    except Grant.DoesNotExist:
        messages.info("You have no Applications connected to your account")
        return HttpResponseRedirect(reverse('home'),
                                RequestContext(request))

    context = {}
    context['my_apps'] = granted

    return render(request, 'accounts/myapps.html',
                  {'my_apps':      granted,
                   'owner':        request.user})
