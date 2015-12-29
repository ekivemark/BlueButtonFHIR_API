"""
developeraccount
FILE: user
Created: 7/6/15 9:39 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import *

from django.shortcuts import (render,
                              render_to_response,
                              redirect)
from django.template import RequestContext
from django.views.generic.edit import *

from accounts.decorators import session_master
from accounts.forms.user import (User_EditForm, Verify_Mobile)
from accounts.models import (User,
                             ValidSMSCode)
from accounts.views.sms import ValidSMSCode
from apps.v1api.models import Crosswalk

@session_master
@login_required()
def verify_phone(request):
    # Verify Mobile Phone for Multi-Factor Authentication

    status = ""

    u = User.objects.get(email=request.user.email)
    form = Verify_Mobile()
    if settings.DEBUG:
        print("In accounts.views.user.verify_phone")
        print("User:", u)

    if request.POST:
        form = Verify_Mobile(request.POST)
        if form.is_valid():
            vc = ValidSMSCode.objects.get(user=u, sms_code=form.cleaned_data['verify_code'])
            if settings.DEBUG:
                print("compare codes",
                      vc.sms_code,"|",
                      form.cleaned_data['verify_code'],
                      )
            if form.cleaned_data['verify_code'] == vc.sms_code:
                if settings.DEBUG:
                    print("Codes Match:", vc)
                u.verified_mobile = True
                u.save()
                return HttpResponseRedirect(reverse('accounts:manage_account'),
                                        RequestContext(request))

    else:
        form = Verify_Mobile()
        trigger = ValidSMSCode.objects.create(user=u)
        if str(trigger.send_outcome).lower() != "fail":
            messages.success(request,
                         "A Verification message was sent to your mobile phone.")
            status = "Text Message Sent"
        else:
            messages.error(request,
                       "There was a problem sending your pin code. Please try again.")
            status = "Send Error"

        if settings.DEBUG:
            print("Trigger in the GET:", trigger)

    return render(request, 'accounts/verify_code.html',
                      {'form': form,
                       'email': u.email})

@session_master
@login_required()
def user_edit(request):
    if settings.DEBUG:
        print(request.user)
        print("Entering User Edit with:%s" % request.user)

    access_field = settings.USERNAME_FIELD

    u = User.objects.get(**{access_field: request.user})
    if settings.DEBUG:
        print("User returned:", u, "[", u.first_name, " ", u.last_name,
              "]")

    form = User_EditForm(data=request.POST or None, instance=u)

    if request.POST:
        form = User_EditForm(request.POST, instance=request.user)
        if form.is_valid():
            # form.save()
            if settings.DEBUG:
                print("Form is valid - current record:", u)

            u.email = form.cleaned_data['email']
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.mobile = form.cleaned_data['mobile']
            u.carrier = form.cleaned_data['carrier']
            u.notify_activity = form.cleaned_data['notify_activity']
            if u.verified_mobile == True:
                # Only set MFA is verified_mobile is True
                # verified_mobile is set in verify_phone()
                u.mfa = form.cleaned_data['mfa']
            else:
                if u.notify_activity == "T":
                    # Unset to "E" because phone is not verified
                    u.notify_activity = "E"
                u.mfa = False
            if settings.DEBUG:
                print("Updated to:", u)
            u.save()

            return HttpResponseRedirect(reverse('accounts:manage_account'),
                                        RequestContext(request))
        else:
            if settings.DEBUG:
                print("Form is invalid")

            messages.error(request, "There was an input problem.")
            return render(request, 'accounts/user_edit.html',
                          {'form': form})

    else:
        u = User.objects.get(**{access_field:request.user})
        if settings.DEBUG:
            print("in the get with User:", u.first_name, " ", u.last_name,
                  " ", u.mobile)
        form = User_EditForm(
            initial={'email': u.email,
                     'first_name': u.first_name,
                     'last_name': u.last_name,
                     'mobile': u.mobile,
                     'carrier': u.carrier,
                     'mfa': u.mfa,
                     'notify_activity': u.notify_activity})
        if settings.DEBUG:
            print("Not in the post in the get")
        return render(request, 'accounts/user_edit.html',
                      {'form': form,
                       'email': u.email})


@login_required()
def Get_ID(Look_for="UUID", Find_with=""):
    """

    :param Look_for: "ICODE" or "UUID"

    :param Find_with: Code to search for
    :return: Code or empty string

    Default is to look for UUID and return ICODE
    """
    if Find_with == "":
        # return blank if no code to search for
        return ""

    looking_for = ""
    if Look_for.upper() == "ICODE":
        looking_for = "ICODE"
    else:
        looking_for = "UUID"

    # We have a value type and value to search for and a

    lu = {}

    luv = ""
    result = ""

    if looking_for == "ICODE":
        try:
            luv = Crosswalk.objects.get(guid=Find_with)
            result = luv.hicn
        except Crosswalk.DoesNotExist:
            result = ""
    else:
        try:
            luv = Crosswalk.objects.get(hicn=Find_with)
            result = luv
        except Crosswalk.DoesNotExist:
            result = ""

    lu = {looking_for: result}
    if settings.DEBUG:
        print("lu returned:", lu)
    return lu


def account_access(request):
    """
    Tell User they have to login with their master account to manage
    their account
    :param request:
    :return:
    """

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE, "in accounts.views.user.account_access")

    context = {}
    return render_to_response('account_access.html',
                              RequestContext(request, context, ))
