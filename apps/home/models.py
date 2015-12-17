# -*- coding: utf-8 -*-
"""
BlueButtonFHIR_API
FILE: home.models
Created: 12/15/15 6:53 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from bbapi.utils import get_current_user

class NewStuff(models.Model):
    """
    Log new items in the application

    """

    title = models.CharField(max_length=250)
    body = models.TextField(max_length=4000,)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=get_current_user)
    created = models.DateTimeField()
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        if not self.author:
            self.author = self.request.user
        return super(NewStuff, self).save(*args, **kwargs)

    def __str__(self):
        # Return the title
        return self.title

    def byline(self):
        # Return Title and Author
        return "%s by %s" % (self.title, self.author)

