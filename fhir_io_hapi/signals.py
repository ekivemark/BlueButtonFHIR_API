#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: signals.py
Created: 2/24/16 1:23 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.dispatch import receiver
from django.db.models.signals import post_save
from oauth2_provider.models import AccessToken


@receiver(post_save, sender=AccessToken)
def write_consent(sender, **kwargs):
    print('Awesome POST_SAVE detected: Saved: {}'.format(kwargs['instance'].__dict__))