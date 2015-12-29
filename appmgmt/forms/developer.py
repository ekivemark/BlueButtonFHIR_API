# -*- coding: utf-8 -*-
"""
bluebuttondev.appmgmt
FILE: developer
Created: 11/2/15 9:34 AM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django import forms
from django.conf import settings

from appmgmt.models import Developer, DEVELOPER_ROLE_CHOICES

class DeveloperForm(forms.ModelForm):
    """
    Model form for Developer with request.user override
    """
    class Meta:
        model = Developer
        fields = ['role' ]
