"""
bbonfhirUser
FILE: backends
Created: 6/22/15 12:49 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from registration import signals
from registration.models import RegistrationProfile

from accounts.models import User


class Backend(object):
    def register(self, request, **kwargs):
        email, password = kwargs['email'], kwargs['password1']
        username = email
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(
            username,
            email,
            password,
            site)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user


class EmailAuthBackend(object):
    """
    A custom authentication backend. Allows users to log in using their email address.
    """

    def authenticate(self, email=None, password=None):
        """
        Authentication method
        """
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None
