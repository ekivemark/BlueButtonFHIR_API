"""
accounts
FILE: forms.py
Created: 6/21/15 8:31 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django import forms
from django.utils.safestring import mark_safe
from registration.forms import (RegistrationFormUniqueEmail,
                                RegistrationFormTermsOfService)

from accounts.models import User


class Email(forms.EmailField):
    def clean(self, value):
        value = value.lower()
        super(Email, self).clean(value)
        try:
            User.objects.get(email=value)
            raise forms.ValidationError(mark_safe(
                "This email is already registered. <br/>Use <a href='/password/reset'>this forgot password</a> link or on the <a href ='/accounts/login?next=/'>login page</a>."))
        except User.DoesNotExist:
            return value


class UserRegistrationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    # email will be no longer become username
    email = Email()

    password1 = forms.CharField(widget=forms.PasswordInput(),
                                label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                label="Repeat your password")

    fields = ['username', 'email', 'password1', 'password2' ]

    def clean_password(self):
        if self.data['password1'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password1']


class RegistrationFormUserTOSAndEmail(UserRegistrationForm,
                                      RegistrationFormUniqueEmail,
                                      RegistrationFormTermsOfService,
                                      ):
    pass


class RegistrationFormTOSAndEmail(
    RegistrationFormUniqueEmail,
    RegistrationFormTermsOfService,
    ):

    pass
