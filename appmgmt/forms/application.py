# -*- coding: utf-8 -*-
"""
bofhirdev
FILE: application
Created: 11/2/15 9:34 AM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django import forms
from django.forms import ModelForm
from django.conf import settings

from appmgmt.models import BBApplication

BOOLEAN_CHOICES = (('1', 'Update'), ('0', 'Keep unchanged'))

class ApplicationForm(forms.ModelForm):
    """
    Model  form for BBApplication with request.user override
    """

    logo = forms.ImageField(required=False)

    class Meta:
        model = BBApplication
        fields = ['name', 'logo',
                  'about',
                  'privacy_url', 'support_url',
                  'client_type', 'authorization_grant_type']

    def __init__(self, *args, **kwargs):
        # self.owner = kwargs['initial']['owner']
        super(ApplicationForm, self).__init__(*args, **kwargs)

    # def save(self, commit=True):
    #     obj = super(ApplicationForm, self).save(False)
    #     obj.owner = self.owner
    #     if settings.DEBUG:
    #         print("In the save", obj, obj.owner.organization)
    #     obj.organization = self.owner.organization
    #
    #     commit and obj.save()
    #     return obj

class Application_Secret_Form(forms.ModelForm):
    """
    Model  form for BBApplication with request.user override
    """
    class Meta:
        model = BBApplication
        fields = ['client_id', 'client_secret', ]

    def __init__(self, *args, **kwargs):
        # self.owner = kwargs['instance']['owner']
        super(Application_Secret_Form, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(Application_Secret_Form, self).save(False)
        obj.owner = self.owner
        commit and obj.save()
        return obj

class Application_Secret(forms.Form):
    """
    Confirm the update of Client_Id and Client_Secret
    """

    confirm = forms.ChoiceField(choices = BOOLEAN_CHOICES,
                                widget = forms.RadioSelect,
                                required=False,
                                help_text="Select 'Update' then click"
                                          " 'Replace' to change the Id and Secret")

class ApplicationDeleteForm(ModelForm):
    """
    Sub-class the ModelForm to provide an instance of 'request'.
    It also saves the object with the appropriate user.
    """
    def __init__(self, request, *args, **kwargs):
        """ Override init to grab the request object. """
        self.request = request
        super(ApplicationDeleteForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        m = super(ApplicationDeleteForm, self).save(commit=False)
        m.owner = self.request.user
        if commit:
            m.save()
        return m
