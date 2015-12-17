"""
bbofuser
FILE: debug
Created: 7/12/15 5:11 PM

A callback routine for overriding Django.debug.toolbar

"""
__author__ = 'Mark Scrimshire:@ekivemark'
from django.conf import settings


def Debug_Toolbar_Display(request):
    # Force to True

    if not settings.DEBUG:
        return False

    return True
