"""
developeraccount
FILE: authenticate
Created: 6/22/15 12:31 PM

Remember to add new classes to accounts.forms.__init__.py


"""
__author__ = 'Mark Scrimshire:@ekivemark'
from django import forms
from django.conf import settings

from accounts.models import User


class AuthenticationForm(forms.Form):
    """
    Login form
    """
    if settings.USERNAME_FIELD == "email":
        email = forms.EmailField(widget=forms.widgets.TextInput)
    else:
        username = forms.CharField(widget=forms.widgets.TextInput)

    password = forms.CharField(widget=forms.widgets.PasswordInput)
    sms_code = forms.CharField(widget=forms.PasswordInput,
                               max_length=5,
                               label="SMS Code",
                               required=False)

    class Meta:
        fields = [settings.USERNAME_FIELD, 'password', 'sms_code']


class SMSCodeForm(forms.Form):
    if settings.USERNAME_FIELD == "email":
        email = forms.EmailField(widget=forms.widgets.TextInput,
                                 label="Enter your email address",
                                 help_text="We will ask for your password in the next step.")
    else:
        username = forms.CharField(widget=forms.widgets.TextInput,
                             label="Please enter your username:",
                             help_text="We will ask for your password in the next step.")


class AuthenticationSMSForm(forms.Form):
    """
    Login form
    """
    if settings.USERNAME_FIELD == "email":
        email = forms.EmailField(widget=forms.widgets.TextInput)
    else:
        username = forms.CharField(widget=forms.widgets.TextInput)
    password = forms.CharField(widget=forms.widgets.PasswordInput)
    sms_code = forms.CharField(widget=forms.PasswordInput,
                               max_length=5,
                               label="SMS Code",
                               required=False)
    send_pin = forms.BooleanField(required=False, widget=forms.HiddenInput
                                  )

    # class Meta:
    #    fields = ['email', 'password', 'sms_code']

    def clean(self):
        cleaned_data = super(AuthenticationSMSForm, self).clean()
        if settings.USERNAME_FIELD == "email":
            u = User.objects.get(email=self.cleaned_data['email'])
        else:
            u = User.objects.get(username=self.cleaned_data['username'])
        mfa = u.mfa
        if settings.DEBUG:
            print(self.cleaned_data)
        if (self.cleaned_data.get('sms_code') == "" and mfa):
            if settings.DEBUG:
                print("MFA:%s for %s" % (mfa, u.email))
            raise forms.ValidationError("Pin Code is required")

        return self.cleaned_data
