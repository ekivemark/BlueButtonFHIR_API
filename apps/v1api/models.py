"""
 models.py in bbapi (BlueButtonFHIR_API)

 .apps.v1api

"""
import collections

from django.conf import settings
from django.db import models

from jsonfield import JSONField

from uuid import uuid4


class Crosswalk(models.Model):
    """

    HICN to UUID Crosswalk and back.
    Linked to User Account

    """
# TODO: Implement PyCrypto to encrypt HICN

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    guid = models.CharField(max_length=40)
    fhir = models.CharField(max_length=40, blank=True )
    fhir_url_id = models.CharField(max_length=80, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    # FHIR = Identifier contained in the Patient Profile
    # fhir_url_id = Identifier used in the patient Profile URL
    # eg. /baseDstu2/Patient/{id}
    # This will allow us to construct a URL to make a call directly to
    # a record, rather than requiring a search

    def save(self, *args, **kwargs):
        created = self.date_created is None
        if not self.pk or created is None:
            if settings.DEBUG:
                print("Overriding Crosswalk save")

            # Assign a GUID with the save
            uid = str(uuid4().urn)[9:]
            # uid4.urn returns string:
            # eg. 'urn:uuid:aec9931c-101b-4803-8666-f047c9159c0c'
            # str()[9:] strips leading "urn:uuid:"
            self.guid = uid

        super(Crosswalk, self).save(*args, **kwargs)


    def __str__(self):
        return "%s %s[%s]" % (self.user.first_name,
                              self.user.last_name,
                              self.guid)


    def get_guid(self):
        # return the uuid
        return self.guid


    def get_email(self):
        # Return the email/username
        return self.user_id


    def get_fhir_url_id(self):
        # Return the patient profile id to add to url
        return self.fhir_url_id

