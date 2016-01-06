"""
BlueButtonFHIR_API
FILE: accounts.utils
Created: 6/27/15 8:39 AM

"""

__author__ = 'Mark Scrimshire:@ekivemark'

import re

from collections import OrderedDict
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import (RequestContext,
                             Context)
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from accounts.choices import (CARRIER_EMAIL_GATEWAY,CARRIER_SELECTION)


def build_message_text(request,context={},
                       template="",
                       extn="txt",
                       ):
    """
    Compose a message to include in an email message
    :param request:
    :param template:
    :param extn: txt, html or sms
            (this becomes the file extension for the template)
            sms is a brief template suitable for SMS Text Messages
    :param email:
    :return:
    """
    # Template files use the Django Template System.

    ctxt = {}
    if context is not None:
        # print("BMT:Context is:", context)
        ctxt = RequestContext(request, context)
        # print("BMT:ctxt with context:", ctxt)

    if request is not None:
        # print("BMT:Request is:", request)
        ctxt = RequestContext(request, ctxt)

    # if settings.DEBUG:
    #     print("BMT:Context ctxt is:", ctxt)

    if template=="":
        template="accounts/messages/account_activity_email"

    source_plate = template + "." + extn

    message = render_to_string(source_plate, ctxt)
    if settings.DEBUG:
        print("Message:",message)

    return message


def cell_email(phone, carrier):
    """
    Receive Phone number and carrier and return sms-email address
    :param phone:
    :param carrier:
    :return: email
    """
    if settings.DEBUG:
        print("Phone:", phone)
    # make sure it is in 10 digit phone number format
    # no + or . or - or ( or )
    if phone == None:
        return None

    # We have a phone number so let's get the email address
    phone_digits = str(phone)
    phone_digits = phone_digits.replace("+1", "")

    # Now we need to check the carrier

    if (carrier == "" or carrier == "NONE" or carrier == None):
        return None

    # We have a phone and a carrier
    if settings.DEBUG:
        print(carrier)
    # lookup email
    carrier_email = dict(CARRIER_EMAIL_GATEWAY)
    carrier_address = carrier_email[carrier]

    email = "%s%s" % (phone_digits, carrier_address)

    return email


def email_mask(email=""):
    """
    mask and potentially shorten an email address
    Useful for communications
    :param email:
    :return:
    """

    if email=="":
        return None

    domain = "@"+email.split("@")[1]
    tld    = "."+domain.split(".")[1]

    if settings.DEBUG:
        print("Domain:",domain)

    result_email = email[:2]+"**" + domain[:2] + "**" + tld[:2] + "**"

    return result_email


def Master_Account(request):
    """
    Check if Master Account by looking for
    :return: True or False
    """

    if request.session["auth_master"]:
            if settings.DEBUG:
                print("Not Master Account:", request.session["auth_device"])
            return False

    return True


def send_activity_message(request,
                          user,
                          subject="",
                          template="",
                          msg="",
                          context={},):
    #Send an email
    # Template files use the Django Template System.

    phone_email_to = cell_email(user.mobile, user.carrier)
    email          = user.email
    from_email     = settings.EMAIL_HOST_USER
    send_to        = []
    message_txt    = ""
    message_html   = ""

    ctx_dict = {}
    if request is not None:
        # if settings.DEBUG:
        #     print("Request is this:",request)
        ctx_dict = RequestContext(request, ctx_dict)

    # User_Model = get_user_model()
    # usermodel = User_Model.objects.get(email=email)
    ctx_dict.update({
        'email': email,
        'user' : user,
        'msg'  : msg,
        'site' : Site.objects.get_current(),
        })

    if context is not None:
        ctx_dict.update(context)

    if settings.DEBUG:
        print("SAM-ctx_dict:", ctx_dict)

    from_email = getattr(settings, 'REGISTRATION_DEFAULT_FROM_EMAIL',
                         settings.DEFAULT_FROM_EMAIL)

    if user.notify_activity.upper() == "E":
        if subject=="":
            subject = settings.APPLICATION_TITLE + " Account Activity for " + email


        # Otherwise we take the subject line passed in to the function
        # Remove any newlines from subject
        subject = ''.join(subject.splitlines())

        # Now we will build the message
        send_to.append(email)
        message_txt = build_message_text(request,
                                         context=ctx_dict,
                                         template=template,
                                         extn="txt")
        if settings.EMAIL_HTML:
            # If True: Generate and attach the HTML version
            message_html = build_message_text(request,
                                              context=ctx_dict,
                                              template=template,
                                              extn="html")
    if user.notify_activity.upper() == "T":
        # Text messages do not have subject lines so we need to reset
        subject = ""
        send_to.append(phone_email_to)

        message_txt = build_message_text(request,
                                         context=ctx_dict,
                                         template=template,
                                         extn="sms")

    if settings.DEBUG:
        print("Sending:", send_to)
        print("Subject:", subject)
        print("Message:", message_txt)

    email = EmailMultiAlternatives(subject,
                                   message_txt,
                                   from_email,
                                   send_to,
                                   )
    if not message_html == "":
        # If html was created we should attach it before message is sent
        email.attach_alternative(message_html, "text/html")

    try:
        result = email.send(fail_silently=False)
        if settings.DEBUG:
            print("Result of Send:", result)
    except:
        result = "FAIL"
        if settings.DEBUG:
            print("Send Failed with:", result)

    return result


def send_sms_pin(email, pin):
    """
    Send a text with an SMS code

    :param email:
    :return:
    """

    subject = ""
    msg = "%s pin:%s" % (settings.APPLICATION_TITLE, pin)
    from_email = settings.EMAIL_HOST_USER
    send_to = []
    send_to.append(email)
    if settings.DEBUG:
        print("Sending %s to %s" % (msg, send_to))

    try:
        result = send_mail(subject, msg, from_email, send_to,
                           fail_silently=False)
        if settings.DEBUG:
            print("Result of send:", result)
    except:
        result = "FAIL"

    if settings.DEBUG:
        print("Send Result:", result)

    return result


def session_device(request, var, Session="auth_device"):
    """
    Set a Session variable if logging in via a subacc
    This will be linked to a decorator to control access to
    sections of the site that will require the master account to be used
    :param request:
    :param session: default is auth_device
    :param var: this should be the var to add to the session
    :return:
    """
    if not var:
        return None
    if Session == "auth_device":
        request.session['auth_device'] = var
    else:
        request.session[Session] = var
    return "%s:%s" % (Session,var)


def string_to_ordereddict(txt):
    #######################################
    # String_To_OrderedDict
    # Convert String to OrderedDict
    # Example String
    #    txt = "OrderedDict([('width', '600'), ('height', '100'),
    # ('left', '1250'), ('top', '980'), ('starttime', '4000'),
    # ('stoptime', '8000'), ('startani', 'random'), ('zindex', '995'),
    # ('type', 'text'), ('title', '#WXR#@TU@@Izmir@@brief_txt@'),
    # ('backgroundcolor', 'N'), ('borderstyle', 'solid'), ('bordercolor', 'N'),
    # ('fontsize', '35'), ('fontfamily', 'Ubuntu Mono'),
    # ('textalign', 'right'), ('color', '#c99a16')])"
    #######################################

    tempDict = OrderedDict()

    od_start = "OrderedDict(["
    od_end = '])'

    first_index = txt.find(od_start)
    last_index = txt.rfind(od_end)

    new_txt = txt[first_index+len(od_start):last_index]
    # print("new_txt:", new_txt)
    # print("First 3:", new_txt[1:-1])


    pattern = r"(\(\'\S+\'\,\ \'\S+\'\))"
    all_variables = re.findall(pattern, new_txt)

    # print("All_var:", all_variables)
    for str_variable in all_variables:
        # print("str_variable", str_variable)
        data = str_variable.split("', '")
        key = data[0].replace("('", "")
        value = data[1].replace("')", "")
        # print("key : %s" % (key))
        # print("value : %s" % (value))
        tempDict[key] = value

    # print(tempDict)
    # print(tempDict['title'])

    return tempDict


def strip_url(domain, www=None):
    """
    receive a URL Field and remove leading http:// or https://
    optionally remove www.
    :param url: eg. http://www.medyear.com
    :param www remove the prefix passed = "www."
    :return:
    """

    u = str(domain)
    u = u.lower()
    check_for_http = "http://"
    check_for_https = "https://"

    result = u.replace(check_for_http, "")
    result = result.replace(check_for_https, "")

    if www != None:
        result = result.replace(www.lower() + ".", "")

    return result


def User_From_Request(request_user=None):
    # Receive request.user
    # Get user model
    # get user key fieldname
    # return user

    if request_user == None:
        return None

    else:
        User = get_user_model()
        access_field = settings.USERNAME_FIELD

        u = User.objects.get(**{access_field:request_user})
        if settings.DEBUG:
            print("User:", u)

        return u


def get_user_record(user):
    """
    Get User using indirect references

    :return:
    """

    if user.is_authenticated():

        access_field = settings.USERNAME_FIELD
        Access_Model = get_user_model()

        u =  Access_Model.objects.get(**{access_field: user})
        if settings.DEBUG:
            print("user field:%s from %s (%s) = %s" % (access_field,
                                                  Access_Model,
                                                  settings.AUTH_USER_MODEL,
                                                  u.get_username()))

    else:

        u = None

    return u