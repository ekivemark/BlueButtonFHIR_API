# -*- coding: utf-8 -*-
"""
BlueButtonFHIR_API
FILE: views
Created: 12/15/15 4:36 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from collections import OrderedDict
from django.http import HttpResponse

import json

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone

from django.views.generic import (TemplateView,
                                  ListView,
                                  CreateView,
                                  DetailView,
                                  UpdateView,
                                  DeleteView)

from .models import NewStuff
from .forms import NewStuffForm

from bbapi.utils import get_current_user


def home_index(request):
    # Show Home Page

    DEBUG = settings.DEBUG_SETTINGS

    if DEBUG:
        print(settings.APPLICATION_TITLE, "in home.views.other.home_index")

    context = {}
    user = request.user

    if user.id == None:
        # user is anon user
        context.update({'organization': ""})
    else:
        pass
        # user is a real user
        #context.update({'organization': request.user.organization})

    return render_to_response('index.html',
                              RequestContext(request, context, ))


def versionView(request):
    """Version information"""
    od = OrderedDict()
    od['request_method'] = request.method
    od['version'] = settings.APPLICATION_TITLE+":"+settings.VERSION_INFO
    od['note'] = "Hello.  Welcome to the " + settings.APPLICATION_TITLE
    return HttpResponse(json.dumps(od, indent=4),
                        content_type="application/json")


class AboutView(TemplateView):
    template_name = 'about.html'


def about(request):
    # Show About Page

    DEBUG = settings.DEBUG_SETTINGS

    if DEBUG:
        print(settings.APPLICATION_TITLE, "in home.views.other.about")

    context = {}
    return render_to_response('about.html',
                              RequestContext(request, context, ))


def what_is_new(request):
    # Show What New Features are launched  (or coming up)

    if settings.DEBUG:
        print("In apps.home.views.what_is_new")

    context = {}
    return render_to_response('whatsnew.html',
                              RequestContext(request, context, ))


class what_is_new_create(CreateView):
    """
    Create NewStuff Record
    :param CreateView:
    :return:
    """
    model = NewStuff
    context_object_name = 'new_stuff'
    #form_class = 'NewStuffForm'
    fields = ['title', 'body',]


class WhatIsNewListView(ListView):

    model = NewStuff
    paginate_by = '5'
    queryset = NewStuff.objects.all().order_by('-modified')
    # remove [:5] to allow more items to be returned.
    # if settings.DEBUG:
    #     print("queryset:", queryset)

    context_object_name = "news"
    template_name = "whatsnew.html"

    def get_context_data(self, **kwargs):
        context = super(WhatIsNewListView, self).get_context_data(**kwargs)
        context['latest'] = NewStuff.objects.all()
        context['now'] = timezone.now()
        context['is_staff'] = get_current_user().is_staff
        if settings.DEBUG:
            print("is staff?", context['is_staff'])
        return context


class WhatIsNewDetailView(DetailView):
    """
    Show individual item
    """

    model = NewStuff
    context_object_name = 'new_stuff'
    #form_class = 'NewStuffForm'
    fields = ['title', 'body',]

    def get_context_data(self, **kwargs):
        context = super(WhatIsNewDetailView, self).get_context_data(**kwargs)
        context['is_staff'] = get_current_user().is_staff
        if settings.DEBUG:
            print("is staff?", context['is_staff'])
        return context


class WhatIsNewUpdateView(UpdateView):
    """
    Update NewStuff Record
    :param UpdateView:
    :return:
    """
    model = NewStuff
    context_object_name = 'new_stuff'
    #form_class = 'NewStuffForm'
    fields = ['title', 'body',]


class WhatIsNewDeleteView(SuccessMessageMixin, DeleteView):
    """
    Delete NewStuff Record with confirmation
    :param DeleteView:
    :return:
    """
    model = NewStuff
    context_object_name = 'new_stuff'
    #form_class = 'NewStuffForm'
    fields = ['title', 'body',]

    success_message = "Deleted Successfully"


    def get_context_data(self, **kwargs):
        context = super(WhatIsNewDeleteView, self).get_context_data(**kwargs)
        context['is_staff'] = get_current_user().is_staff
        if settings.DEBUG:
            print("Delete View: is staff?", context['is_staff'])
        return context


    def get_queryset(self):
        qs = super(WhatIsNewDeleteView, self).get_queryset()
        return qs.filter(author=self.request.user)
