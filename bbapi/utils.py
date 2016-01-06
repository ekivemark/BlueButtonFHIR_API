"""
bbofuser
FILE: utils
Created: 6/16/15 12:11 AM
Basic conversion tools
"""
__author__ = 'Mark Scrimshire:@ekivemark'

from threading import local


_user = local()

class CurrentUserMiddleware(object):
    ###
    ### Add to MIDDLEWARE_CLASSES after Authentication middleware
    ###
    def process_request(selfself,request):
        _user.value = request.user


def get_current_user():
    return _user.value


def str2bool(inp):
    output = False
    if inp.upper() == "TRUE":
        output = True
    elif inp.upper() == "FALSE":
        output = False

    return output


def str2int(inp):
    output = 0 + int(inp)

    return output


