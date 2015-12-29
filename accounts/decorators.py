"""
bbofuser
FILE: decorators
Created: 8/6/15 1:23 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'


from functools import wraps

from django.contrib.auth.decorators import (user_passes_test,
                                            PermissionDenied)
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext


# USE THIS DECORATOR
def session_master(func):
    # Is the account using the master profile or a subacc
    # request.session['auth_master'] only set on master account
    def decorated(request, *args, **kwargs):
        if 'auth_master' in request.session:
            # print("request.session:", request.session['auth_master'])
            # We have the Request Session value we need so get on with it
            return func(request, *args, **kwargs)
        else:

            # print("Request session:", "NOT AUTH_MASTER")
            # No access from this account so send to a warning page
            messages.error(request,"Access to this feature is not available \
                                    from this account. Use Your Master Account")
            return HttpResponseRedirect(reverse('accounts:account_access'),
                                                RequestContext(request,
                                                               *args,
                                                               **kwargs))
    return decorated



# Not working
def session_master_required(function=None,
                            redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user has auth_master="True"
    in request.session,
    redirecting to the log-in page if necessary.
    """
    print("Function:", function)
    result = False
    if True==True: #function.request.session['auth_master']:
        if True==True: #function.request.session['auth_master'].upper()=="TRUE":
            result = function(request, *args, **kwargs)
    actual_decorator = user_passes_test(
        result,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator