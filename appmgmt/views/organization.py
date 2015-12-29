"""
bofhirdev.apps.appmgmt
FILE: views.py
Created: 10/28/15 5:20pm

"""

import random

from django import forms

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import (reverse,
                                      reverse_lazy)
from django.http import (HttpResponse,
                         JsonResponse,
                         HttpResponseRedirect)
from django.shortcuts import render
from django.template import RequestContext
from django.views.generic import (DetailView,
                                  UpdateView)
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from appmgmt.models import (Organization,
                            BBApplication,
                            Developer)

from appmgmt.forms import OrganizationForm

# We need an app management set of transactions here

# Organization Display
class MyOrganizationListView(ListView):
    """
    View for Organizations

    :param ListView:
    :return:
    """

    model = Organization
    template_name = 'organization_list.html'

    def get_queryset(self):
        if settings.DEBUG:
            print("Queryset User:", self.request.user)
        qs = super(MyOrganizationListView, self).get_queryset()

        if settings.DEBUG:
            result = qs.filter(owner=self.request.user).values()
            print("qs filter:", result)

        return qs.filter(owner=self.request.user).values()
    # def get_context_data(self, **kwargs):
    #     context = super(MyOrganizationListView, self).get_context_data(**kwargs)

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(MyOrganizationListView, self).get_context_data(**kwargs)
        # add in a QuerySet of all Applications

        org_name = context['object_list'][0]['id']

        context['extra_content'] = {"developer_list":Developer.objects.filter(organization=org_name),
                                    "application_list":BBApplication.objects.filter(organization=org_name)}
        if settings.DEBUG:
            print("Context:", context)
            print("Developers:", context['extra_content']['developer_list'])

        return context


class MyOrganizationUpdateView(UpdateView):
    """
    Edit view for Organization

    """
    model = Organization
    fields = ['name', 'domain' ]

    context_object_name = "organization"

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(MyOrganizationUpdateView, self).get_context_data(**kwargs)
        # add in a QuerySet of all Applications
        context['extra_content'] = {"application_list":BBApplication.objects.filter(organization=self.kwargs['pk']),
                                    "developer_list":Developer.objects.filter(organization=self.kwargs['pk'])}
        if settings.DEBUG:
            print("Context:", context)

        return context


@login_required
def My_Organization_Create(request):
    """
    If no organization attached to user we need to create one.
    Organization and Domain must be UNIQUE

    :param request:
    :return:
    """

    User = get_user_model()
    access_field = settings.USERNAME_FIELD

    u = User.objects.get(**{access_field:request.user})
    if settings.DEBUG:
        print("User:", u)

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            org = form.save(commit=False)
            org.owner = request.user
            org.save()

            # Set to Account Owner Value from DEVELOPER_ROLE_CHOICES ['1']
            dev_team = Developer(member=request.user,
                                 role='1',
                                 organization=org)
            dev_team.save()

            # Update Organization in Account.User
            u.organization = org
            u.save()

            # Check
            return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))
    else:

        form = OrganizationForm(initial={'owner': request.user})

    return render(request, 'appmgmt/organization_form.html', {'form': form})


class MyOrganizationCreate(CreateView):
    """
    Create for Organization
    """

    model = Organization
    form_class = OrganizationForm
    # fields = ['name', 'domain', 'developers',]

    def get_initial(self):
        self.initial.update({ 'owner': self.request.user})
        return self.initial

    def clean(self, request, form):
        try:
            Organization.objects.get(name__iexact=form.cleaned_data['name'].lower(),
                                     domain__iexact=form.cleaned_data['domain'].lower())
            # if get this far we have a duplicate
            problem = "Organization and domain already registered!"
            #form.add_error('name', problem)
            #form.add_error('domain', problem)
            messages.error(request, problem)
            # raise forms.ValidationError(problem)

        except Organization.DoesNotExist:
            # there wasn't a case insensitive match
            pass

        return form

    def form_valid(self, form):
        # do things if the form is valid
        if self.clean(self.request, form):
            return super(MyOrganizationCreate, self).form_valid(form)
        else:
            return super(MyOrganizationCreate, self).form_invalid(form)

# Organization Update


