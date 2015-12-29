# -*- coding: utf-8 -*-
"""
BlueButtonDev.appmgmt
FILE: utils
Created: 12/2/15 8:09 PM

"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.contrib import messages

from .models import DEVELOPER_ROLE_CHOICES

from django.conf import settings
def Choice_Display(role):
    """
    Receive a string of the current role
    Lookup in DEVELOPER_ROLE_CHOICES
    Return the String
    :param role:
    :return:
    """
    result = dict(DEVELOPER_ROLE_CHOICES).get(role)

    if role == "None":

        return
    else:
        return result

class MessageMixin(object):
    """
    Make it easy to display notification messages when using Class Based Views.
    """
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).delete(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).form_valid(form)