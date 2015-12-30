# -*- coding: utf-8 -*-
"""
bofhirdev
FILE: trust
Created: 11/2/15 8:20 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django import forms

TRUST_BUNDLE_CHOICE = (('', 'None'),
                       ('TEST','test'),
                       ('NATE', 'National Association for Trusted Exchange'),
                       ('DIRECTTRUST', 'DirectTrust'))

class TrustForm(forms.Form):
    """
    Get Data for Trust Call

    """

    trust_bundle = forms.ChoiceField(choices=TRUST_BUNDLE_CHOICE)
    trust_domain = forms.CharField(max_length=100,
                                   label="Trusted Application Domain")
    owner_email = forms.EmailField(label="Trusted Application Owner Email")
    shared_secret = forms.CharField(max_length=5124,
                                    widget=forms.Textarea(attrs={'cols': 80,
                                                                 'rows': 10}),
                                    label="Trust Bundle Entity Secret")

    # class Meta:
    #     fields = ['trust_bundle', 'trust_domain', 'administrator_email']