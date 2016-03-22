# -*- coding: utf-8 -*-
"""
BlueButtonFHIR_API
FILE: admin_disable
Created: 12/16/15 8:05 AM


"""
from django.forms import Textarea

__author__ = 'Mark Scrimshire:@ekivemark'

from django import forms
from django.contrib import admin

from django.conf import settings

from .forms import NewStuffForm
from .models import NewStuff

class NewStuffAdmin(admin.ModelAdmin):
    """
    Admin form for NewStuff model
    """

    form = NewStuffForm

    list_display = ('title', 'body', 'author')
    readonly_fields = ('created', 'modified', 'author')

    def save_model(self, request, obj, form, change):
        """
        When creating a new object, set the creator field.
        """
        if settings.DEBUG:
            print("Saving model with ", request.user)
            print("mode=", change)
        if not change:
            obj.author = request.user

        obj.save()


admin.site.register(NewStuff, NewStuffAdmin)
