# -*- coding: utf-8 -*-
"""
bluebuttondev.appmgmt
FILE: organization
Created: 11/2/15 9:34 AM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django import forms
from django.conf import settings

from appmgmt.models import Organization

class OrganizationForm(forms.ModelForm):
    """
    Model  form for Organization with request.user override
    """
    class Meta:
        model = Organization
        fields = ['name', 'domain', ]

    # def __init__(self, *args, **kwargs):
    #     if settings.DEBUG:
    #         print("args:", args)
    #     self.owner = kwargs['initial']['owner']
    #     super(OrganizationForm, self).__init__(*args, **kwargs)


    def clean(self):
        match = False
        match_name = False
        match_domain = False
        problem = " already registered!"
        try:
            found_name = Organization.objects.get(name__iexact=self.cleaned_data['name'].lower())
            match = True
            match_name = True
            if settings.DEBUG:
                print("found:", found_name)
            self.add_error('name', "Organization name" + problem)

        except Organization.DoesNotExist:
            match = False

        try:
            found_domain = Organization.objects.get(domain__iexact=self.cleaned_data['domain'].lower())
            match = True
            match_domain = True
            if settings.DEBUG:
                print("found", found_domain)
            self.add_error('name', "Domain " + problem)

        except Organization.DoesNotExist:
            match = False

        # if get this far we have a duplicate
        if match_name and match_domain:
            problem = "Organization and domain already registered!"
            # messages.error(self.request, problem)
            raise forms.ValidationError(problem)

        return self.cleaned_data


    # def save(self, commit=True):
    #     obj = super(OrganizationForm, self).save(False)
    #     obj.owner = self.owner
    #     commit and obj.save()
    #     return obj
