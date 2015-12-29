"""
developeraccount
FILE: sms
Created: 7/5/15 12:45 PM

All SMS Related views

"""
__author__ = 'Mark Scrimshire:@ekivemark'

import ldap3

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (login as django_login,
                                 authenticate)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django.shortcuts import (render_to_response)
from django.template import RequestContext
from django.utils import timezone
from django.utils.safestring import mark_safe

from accounts.utils import (send_activity_message,
                            cell_email)
from accounts.forms.authenticate import (AuthenticationForm,
                                         SMSCodeForm)
from accounts.views.ldap import validate_ldap_user
from accounts.models import (User,
                             ValidSMSCode)

from accounts.utils import (session_device,
                            Master_Account)


def validate_user(request, email):
    """

    :param request:
    :param email:
    :return:
    We will lookup the email address in LDAP and then find in accounts.user
    """

    # step 1 is to look up email in LDAP

    result = validate_ldap_user(request, email)
    # Check the result for the mail field
    # Compare to the email received

    if settings.DEBUG:
        print("ldap email check:", result)
    # step 2 is to look up email in accounts.User

    if result[:5] == "ERROR" and not "@" in result :
        # There was a problem with reaching the LDAP Server
        if settings.DEBUG:
            print("ldap email returned error")
        email_match = False

    else:
        print("LDAP Returned:", result)
        # We got something back from LDAP so we check it for a match
        if result.lower() == email.lower():
            email_match = True
        else:
            email_match = False
            # Set an error message
            messages.error(request,
                            mark_safe("Your email was not recognized. Do you need to "
                                      "<a href='/registration/register/'>register</a>?"))

    if settings.DEBUG:
        print("Match?:", email_match)

    return email_match


def make_local_user(request, email):
    """

    :param request:
    :param email:
    :return:

    get email address of a user validated via LDAP

    pull user details from LDAP

    create local user account using email address as key

    return user

    """
    messages.error(request,mark_safe("You are registered on MyMedicare.gov. "
                           "\nBut not registered for BlueButton."
                           " \nPlease complete the "
                           "<a href='/registration/register/'>"
                                     "BlueButton Registration</a>"))

    result = HttpResponseRedirect("/registration/register/", request)

    return result


def validate_sms(access_key, smscode):
    if settings.DEBUG:
        print("%s, %s" % (access_key, smscode))

    access_field = settings.USERNAME_FIELD

    mfa_on = False
    try:
        u = User.objects.get(**{access_field: access_key})
        if settings.DEBUG:
            print("Getting ", access_field, " with", access_key, ".",
                  "found email:", u.email, ".")
        mfa_on = u.mfa
        vc = ValidSMSCode.objects.get(user=u, sms_code=smscode)
        if settings.DEBUG:
            print("vc: %s - %s" % (vc, mfa_on))
        now = timezone.now()
        if vc.expires < now:
            vc.delete()
            return False
    except(User.DoesNotExist):
        if settings.DEBUG:
            print("User does not exist")
        return False
    except(ValidSMSCode.DoesNotExist):
        if not mfa_on:
            if settings.DEBUG:
                print("MFA disabled", "")
            return True
        else:
            if settings.DEBUG:
                print("ValidSMS does not exist")
            return False
    if settings.DEBUG:
        print("Success! Deleting %s" % vc)
    vc.delete()
    return True


def sms_login(request, *args, **kwargs):

    # Check session variables to find information carried forward.
    access_field = settings.USERNAME_FIELD
    # This is the key field name. Probably username or email

    if access_field in request.session:
        if request.session[access_field] != "":
            access_key = request.session[access_field]
        else:
            access_key = ""
    else:
        access_key = ""
    if settings.DEBUG:
        # print(request.GET)
        print("SMS_LOGIN.GET:", access_field, ":[%s]" % (access_key))
        # print(request.POST)
        print(args)

    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if request.POST['login'].lower() == 'resend code':
            if settings.DEBUG:
                print("Resending Code for %s" % request.POST[access_field])
            # form = SMSCodeForm(request.POST)
            # form.username = request.POST['username']
            request.session[access_field] = request.POST[access_field]
            return HttpResponseRedirect(reverse('accounts:sms_code'))
        if form.is_valid():
            print("Authenticating...")
            access_key = form.cleaned_data[access_field].lower()
            password = form.cleaned_data['password'].lower()
            sms_code = form.cleaned_data['sms_code']
            if not validate_sms(access_key=access_key, smscode=sms_code):
                messages.error(request, "Invalid Access Code.")
                return render_to_response('accounts/login.html',
                                          {'form': AuthenticationForm()},
                                          RequestContext(request))
            # DONE: Trying to handle LDAP Errors. eg. Not available
            try:
                user = authenticate(username=access_key, password=password)
            except (ldap3.LDAPBindError,
                    ldap3.LDAPSASLPrepError,
                    ldap3.LDAPSocketOpenError):
                print("We got an LDAP Error - Bind:",dir(ldap3.LDAPBindError),
                    "\nSASL Prep:", ldap3.LDAPSASLPrepError,
                    "\nSocketOpenError:",ldap3.LDAPSocketOpenError)
                messages.error(request, "We had a problem reaching the Directory Server")
                return render_to_response('accounts/login.html',
                                      RequestContext(request))

            #######

            if user is not None:

                if user.is_active:
                    django_login(request, user)

                    # DONE: Set a session variable to identify as
                    # master account and not a subacc
                    session_device(request,
                                    "True",
                                    Session="auth_master")

                    # DONE: Now Send a message on login
                    if user.notify_activity in "ET":
                        send_activity_message(request,
                                              user)
                    # Otherwise don't send a message

                    return HttpResponseRedirect(reverse('home'))
                else:

                    messages.error(request, "Your account is not active.")
                    return HttpResponseRedirect(reverse('sms_code'))
            else:
                messages.error(request, "Invalid username or password.")
                return render_to_response('accounts/login.html',
                                          {'form': AuthenticationForm()},
                                          RequestContext(request))
        else:
            print("Error with the POST form", )
            return render_to_response('accounts/login.html',
                                      {'form': form},
                                      RequestContext(request))
    else:
        if access_field in request.session:
            access_key = request.session[access_field]
        else:
            access_key = ""
        if settings.DEBUG:
            print("in sms_login. Setting up Form [", access_key, "]")
        form = AuthenticationForm(initial={access_field: access_key, })
    if settings.DEBUG:
        # print(form)
        print("Dropping to render_to_response in sms_login")
    return render_to_response('accounts/login.html', {'form': form},
                              RequestContext(request))


def sms_code(request):

    # Check session variables to find information carried forward.
    access_field = settings.USERNAME_FIELD
    # This is the key field name. Probably username or email


    if access_field in request.session:
        if request.session[access_field] != "":
            access_key = request.session[access_field]
        else:
            access_key = ""
    else:
        access_key = ""
    status = "NONE"
    if settings.DEBUG:
        print("in accounts.views.sms.sms_code")

    if request.method == 'POST':
        if request.POST.__contains__(access_field):
            access_key = request.POST[access_field].lower()
            print("POST ", access_field ,"on entry:[%s]" % (access_key))
        else:
            if access_field in request.session:
                if request.session[access_field] != "":
                    access_key = request.session[access_field].lower()
            else:
                access_key = ""
        if settings.DEBUG:
            #print("request.POST:%s" % request.POST)
            print("%s:%s" % (access_field, access_key))

        form = SMSCodeForm(request.POST)

        if form.is_valid():
            if not validate_user(request, form.cleaned_data[access_field].lower()):
                request.session[access_field] = ""
                # We had a problem
                # Message error was set in validate_user function
                status = access_field + " not Recognized"
                return HttpResponseRedirect(reverse('accounts:sms_code'))
            else:
                if settings.DEBUG:
                    print("Valid form with a valid ", access_field)
                # True if email found in LDAP
                try:
                    u = User.objects.get(**{access_field:form.cleaned_data[access_field].lower()})
                    if settings.DEBUG:
                        print("returned u:", u)
                    # u=User.objects.get(username=form.cleaned_data['username'].lower())
                    mfa_required = u.mfa
                    email = u.email
                    if settings.DEBUG:
                        print("Require MFA Login:%s" % mfa_required)
                    if u.is_active:
                        # posting a session variable for login page
                        request.session[access_field] = access_key
                        if mfa_required:
                            trigger = ValidSMSCode.objects.create(user=u)
                            if str(trigger.send_outcome).lower() != "fail":
                                messages.success(request,
                                                 "A text message was sent to your mobile phone.")
                                status = "Text Message Sent"
                            else:
                                messages.error(request,
                                               "There was a problem sending your pin code. Please try again.")
                                status = "Send Error"
                                return HttpResponseRedirect(
                                    reverse('accounts:sms_code'))
                        else:
                            messages.success(request,
                                             "Your account is active. Continue Login.")
                            status = "Account Active"
                    else:
                        request.session[access_field] = ""
                        messages.error(request,
                                       mark_safe("Your account is inactive. If you recently registered to use BlueButton"
                                       "\nplease check your email for an activation link."))
                        status = "Inactive Account"
                        return HttpResponseRedirect(
                            reverse('accounts:sms_code'))
                except(User.DoesNotExist):
                    # User is in LDAP but not in User Table
                    #u = make_local_user(request,
                    #                    email=form.cleaned_data['email'].lower())
                    # DONE: Point to Registration Page
                    # DONE: Redirect user to educate, acknowledge, validate step
                    messages.error(request,mark_safe("You are registered on MyMedicare.gov. "
                                                     "\nBut not registered for BlueButton."
                                                     " \nPlease complete the <a href='/registration/register/'>BlueButton Registration</a>"))

                    request.session[access_field] = ""
                    args = {}
                    args[access_field] = form.cleaned_data[access_field].lower()
                    return HttpResponseRedirect("/accounts/learn/0/", access_key)

                    # messages.error(request, "You are not recognized.")
                    # status = "User UnRecognized"
                    #return HttpResponseRedirect(
                    #    reverse('accounts:sms_code'))
                    # except(UserProfile.DoesNotExist):
                    #     messages.error(request, "You do not have a user profile.")
                    #     return HttpResponseRedirect(reverse('sms_code'))
                if settings.DEBUG:
                    print("dropping out of valid form")
                    print("Status:", status)
                    print("%s: %s" % (access_field, access_key))
                    # Change the form and move to login

            form = AuthenticationForm(initial={access_field: access_key})
            args = {}
            args['form'] = form
            return HttpResponseRedirect(reverse('accounts:login'), args)
        else:
            if settings.DEBUG:
                print("invalid form")
            # need to make form.username a variable
            form.username = access_key

            return render_to_response('accounts/smscode.html',
                                      RequestContext(request,
                                                     {'form': form}))
    else:
        if access_field in request.session:
            if request.session[access_field] != "":
                access_key = request.session[access_field]
            else:
                access_key = ""
        else:
            access_key = ""
        if settings.DEBUG:
            print("setting up the POST in sms_code [", access_key, "]")
        form = SMSCodeForm(initial={access_field: access_key, })
        # need to make form.username a variable
        if settings.USERNAME_FIELD == "email":
            form.email = access_key
        else:
            form.username = access_key
        if settings.DEBUG:
            print("form ", access_field, form)
            print("In the sms_code.get")

    if settings.DEBUG:
        print("form:", form)
        print("Dropping to render_to_response in sms_code")
    return render_to_response('accounts/smscode.html', {'form': form},
                              RequestContext(request))
