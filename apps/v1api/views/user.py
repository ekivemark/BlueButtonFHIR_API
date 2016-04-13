#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: apps.v1api.views.user

Created: 4/12/16 10:47 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import (reverse_lazy,
                                      reverse)
from django.shortcuts import render_to_response
from django.template import RequestContext

from accounts.utils import get_user_record
from ..models import Crosswalk

from fhir.utils import kickout_404


@login_required
def me(request):
    """
    Return user information
    :param request:
    :return:
    """

    User = get_user_model()
    u = get_user_record(request.user)

    try:
        xwalk = Crosswalk.objects.get(user=request.user.id)
    except Crosswalk.DoesNotExist:
        reason = "Unable to find Patient ID for user:%s[%s]" % (request.user,
                                                                request.user.id)
        messages.error(request, reason)
        return kickout_404(reason)

    context = OrderedDict()
    context['template'] = 'v1api/user.html'
    context['profile'] = "User"
    context['get_fmt'] = "json"
    context['name'] = u.username
    context['first_name'] = u.first_name
    context['last_name'] = u.last_name
    context['email'] = u.email
    context['fhir_urlid'] = xwalk.fhir_url_id
    context['text'] = "<div>Name: <b>%s %s</b> (%s)<br/>" \
                      "Email: %s<br/>" \
                      "FHIR ID: %s</div>" % (context['first_name'], context['last_name'],
                                             context['name'], context['email'],
                                             context['fhir_urlid'])

    return render_to_response(context['template'],
                              RequestContext(request,
                                             context))

