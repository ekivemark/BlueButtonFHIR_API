"""
bofhirdev.apps.appmgmt
FILE: views.py
Created: 10/28/15 5:20pm

"""

import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.http import (HttpResponse,
                         JsonResponse,
                         HttpResponseRedirect)
from django.shortcuts import (render,
                              render_to_response)
from django.template import RequestContext
from django.views.generic import (DetailView,
                                  UpdateView)
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from appmgmt.models import (Organization, BBApplication)
from appmgmt.forms import OrganizationForm

# We need an app management set of transactions here

def home_index(request):
    # Show Home Page for appmgmt

    DEBUG = settings.DEBUG_SETTINGS

    if DEBUG:
        print(settings.APPLICATION_TITLE, "in appmgmt.views.main.home_index")

    context = {}
    return render_to_response('index.html',
                              RequestContext(request, context, ))



# User detail view
class UserDetailView(DetailView):

    context_object_name = "user"
    model = settings.AUTH_USER_MODEL

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserDetailView, self).get_context_data(**kwargs)
        # add in a QuerySet of all Organizations
        context['organization_list'] = Organization.objects.filter(owner=self.request.user)
        return context

