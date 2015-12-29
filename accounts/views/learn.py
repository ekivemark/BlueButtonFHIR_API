"""
bbofuser
FILE: learn
Created: 8/10/15 9:18 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext


def learn_0(request):
    # Show Education Page 0

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE, "in accounts.views.learn.learn_0")

    context = {}
    return render_to_response('accounts/education_0.html',
                              RequestContext(request, context, ))

def learn_1(request):
    # Show Education Page 1

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE, "in accounts.views.learn.learn_1")

    context = {}
    return render_to_response('accounts/education_1.html',
                              RequestContext(request, context, ))


def learn_2(request):
    # Show Home Page


    if settings.DEBUG:
        print(settings.APPLICATION_TITLE, "in accounts.views.learn.learn_2")

    context = {}
    return render_to_response('accounts/education_2.html',
                              RequestContext(request, context, ))

def what_is_new(request):
    # Show What New Features are launched  (or coming up)

    if settings.DEBUG:
        print("In accounts.views.learn.what_is_new")

    context = {}
    return render_to_response('whatsnew.html',
                              RequestContext(request, context, ))