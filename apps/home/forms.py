# -*- coding: utf-8 -*-
"""
BlueButtonFHIR_API
FILE: apps.home.forms
Created: 12/16/15 12:45 AM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django import forms
from django.db import models

from django.forms import Textarea

from apps.home.models import NewStuff


class NewStuffUserForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        return super(NewStuffUserForm, self).__init__(*args, **kwargs)

    # Overriding save allows us to add the user from the request
    def save(self, *args, **kwargs):
        kwargs['commit']=False
        obj = super(NewStuffUserForm, self).save(*args, **kwargs)

        if self.request:
            obj.author = self.request.user
        obj.save()
        return obj



class NewStuffForm(forms.ModelForm):
    """
    used by Create and Update View for NewStuff

    """

    # title = forms.CharField()
    # body = forms.CharField(widget=forms.Textarea)


    class Meta:
        model = NewStuff
        fields = ['title', 'body']
        widgets = {'parameters': Textarea(attrs={'cols': 60, 'rows': 4}),
                   }

