"""
 Developer views
 (c) 2015 - Mark Scrimshire - @ekivemark
"""
__author__ = 'Mark Scrimshire:@ekivemark'

# DONE Activate Account
# DONE: accounts/profile Landing Page.
import ast
import json

from collections import OrderedDict
from django.core import serializers
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required, settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth import (login as django_login,
                                 authenticate,
                                 logout as django_logout, get_user_model)
from django.views.generic.detail import DetailView

from accounts.admin import UserCreationForm
from accounts.decorators import (session_master,
                                 session_master_required)
from accounts.forms.authenticate import AuthenticationForm
from accounts.forms.register import RegistrationForm
from apps.v1api.models import (Crosswalk)
from accounts.utils import (get_user_record,
                            cell_email,
                            send_activity_message)
from appmgmt.models import Organization, Developer

from ..utils import string_to_ordereddict

#from apps.subacc.models import Device
#from apps.subacc.utils import Master_Account

#from apps.secretqa.models import QA


def login(request):
    """
    Login view

    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(email=request.POST['email'],
                                password=request.POST['password'])
            if user is not None:
                if settings.DEBUG:
                    print("User is not Empty!")
                if user.is_active:
                    django_login(request, user)
                    return redirect('/')
    else:
        form = AuthenticationForm()
    return render_to_response('registration/login.html', {
        'form': form,
    }, context_instance=RequestContext(request))


def register(request):
    """
    User registration view.
    """

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse_lazy('home'))
    else:
        form = RegistrationForm()
    context = {'form': form}

    return render_to_response('register.html',
                              context_instance=RequestContext(request,
                                                              context,))


def logout(request):
    """
    Log out view
    """
    # DONE: Change redirection based on whether subacc or user
    if 'auth_device' in request.session:
        mode = "subacc"
    else:
        mode = "user"

    django_logout(request)
    if mode == "subacc":
        return redirect(reverse_lazy('api:home'))
    return redirect(reverse_lazy('home'))


def home_index(request):
    # Show Home Page

    DEBUG = settings.DEBUG_SETTINGS

    if DEBUG:
        print(settings.APPLICATION_TITLE, "in accounts.views.other.home_index")

    context = {}
    return render_to_response('index.html',
                              RequestContext(request, context, ))


def about(request):
    # Show About Page

    DEBUG = settings.DEBUG_SETTINGS

    if DEBUG:
        print(settings.APPLICATION_TITLE, "in accounts.views.other.about")

    context = {}
    return render_to_response('about.html',
                              RequestContext(request, context, ))


def agree_to_terms(request):
    # Agree to Terms
    # Register for account

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE,
              "in accounts.views.agree_to_terms")

    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse_lazy('home'))
    else:
        form = UserCreationForm()

    context = {'form': form, }
    #   return render_to_response('developer/agree_to_terms_user.html', RequestContext(request, context,))
    return render_to_response(reverse_lazy('accounts:register'),
                              RequestContext(request, context, ))


@session_master
@login_required
def manage_account(request):
    # Manage Accounts entry page
    # Check user record for is_developer or is_user

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE,
              "in accounts.views.manage_account")

    # get_user_record uses request.user to lookup AUTH_USER_MODEL/get_user_model()
    # to retrieve the user record

    user = get_user_record(request.user)
    if settings.DEBUG:
        print("is this a Developer?", user.is_developer, "[", request.user.is_developer ,"]")
        print("is this a Beneficiary?", user.is_user, "[", request.user.is_user ,"]")

    if request.user.is_developer:
        # Do the developer version of manage_account
        page_render = manage_developer(request)

    else:
        # Do the user version of manage_account
        page_render = manage_user(request)


    return page_render


@session_master
@login_required
def manage_user(request):
    # Manage Accounts entry page

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE,
              "in accounts.views.manage_user via manage_account")

    # get_user_record uses request.user to lookup AUTH_USER_MODEL/get_user_model()
    # to retrieve the user record

    user = get_user_record(request.user)
    if settings.DEBUG:
        print("is this a Developer?", user.is_developer, "[", request.user.is_developer ,"]")
        print("is this a Beneficiary?", user.is_user, "[", request.user.is_user ,"]")

    mfa_address = cell_email(user.mobile, user.carrier)


    context = {"user": user,
               "mfa_address": mfa_address,
               }

    return render_to_response('accounts/manage_user.html',
                              RequestContext(request, context, ))


@session_master
@login_required
def manage_developer(request):
    # Manage Developer Account entry page

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE,
              "in accounts.views.manage_developer via manage_account")
    account_model = get_user_model()
    access_field = settings.USERNAME_FIELD
    user = get_user_record(request.user)

    mfa_address = cell_email(user.mobile, user.carrier)
    try:
        org = Organization.objects.get(name=request.user.organization)
    except Organization.DoesNotExist:
        org = {}
        # org.update({'name': ""})


    # get my Developer role
    try:
        my_dev = Developer.objects.get(member=user)
        my_role = my_dev.role
        if my_dev.role in ['1','2']:
            org_owner = True
        else:
            org_owner = False
    except Developer.DoesNotExist:
        my_dev = {}
        my_role = ""
        org_owner = False

    # get the dev team members
    try:
        my_team = Developer.objects.filter(organization=user.organization).order_by('role')
    except Developer.DoesNotExist:
        my_team = {}

    # get the email_domain for user
    domain = "@" + user.get_email_domain()
    # get users with the same domain in email address as candidates to add
    try:
        candidates = account_model.objects.filter(email__icontains=domain,
                                                  organization=None)
    except account_model.DoesNotExist:
        candidates = {}

    if settings.DEBUG:
        print("User:", user)
        print("Organization:", org )
        print("My_Dev_Role :", my_dev, "[", my_role, "]")
        print("My_Dev_Team :", my_team)
        print("Candidates  :", candidates)

    context = {"user": user,
               "my_role": my_role,
               "org_owner": org_owner,
               "mfa_address": mfa_address,
               "domain": domain,
               "org": org,
               "my_dev": my_dev,
               "my_team": my_team,
               "candidates": candidates,
               }

#    return render_to_response('accounts/manage_account.html',
#                              RequestContext(request, context, ))

    # Using Alternate manage_account template
    return render_to_response('appmgmt/manage_developer.html',
                              RequestContext(request, context, ))
