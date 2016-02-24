# Create your models here.
# apps.appmgmt.models

# Extend the Django OAuth Provider Application Model
# Author: Mark Scrimshire (c) @ekivemark

import json

from collections import OrderedDict

from django.conf import settings
from django.db import models
from oauth2_provider.models import AbstractApplication
from accounts.choices import DEVELOPER_ROLE_CHOICES
from .choices import APPLICATION_TYPE_CHOICES
from .utils import write_fhir, build_fhir_id

# Modify settings.py wih OAUTH2_PROVIDER_APPLICATION_MODEL=

class BBApplication(AbstractApplication):
    # Extension of the OAuth2 Application to add extra fields.
    # client_id = models.CharField(max_length=100, unique=True,
    #                              default=generate_client_id, db_index=True)
    # user = models.ForeignKey(AUTH_USER_MODEL,
    #                          related_name="%(app_label)s_%(class)s")
    # help_text = _("Allowed URIs list, space separated")
    # redirect_uris = models.TextField(help_text=help_text,
    #                                  validators=[validate_uris], blank=True)
    # client_type = models.CharField(max_length=32, choices=CLIENT_TYPES)
    # authorization_grant_type = models.CharField(max_length=32,
    #                                             choices=GRANT_TYPES)
    # client_secret = models.CharField(max_length=255, blank=True,
    #                                  default=generate_client_secret,
    #                                  db_index=True)
    # name = models.CharField(max_length=255, blank=True)
    # skip_authorization = models.BooleanField(default=False)

    organization = models.ForeignKey('Organization',
                                     blank=True,
                                     null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              blank=True,
                              null=True)
    logo = models.ImageField(upload_to='.',
                             blank=True,
                             null=True)
    about = models.TextField(null=True,
                             blank=True,
                             verbose_name="About this app",
                             editable=True)
    agree = models.BooleanField(verbose_name='Agreed to T&Cs',
                                default=False)
    agree_version = models.CharField(max_length=10,
                                     verbose_name='T&C Version',
                                     blank=True,
                                     null=True)
    agree_date = models.DateTimeField(verbose_name='Date T&C Agreed',
                                      blank=True,
                                      null=True,
                                      default=None)
    app_type = models.CharField(max_length=8,
                                choices=APPLICATION_TYPE_CHOICES,
                                verbose_name="Application Type",
                                blank=True,
                                null=True)
    privacy_url = models.URLField(blank=True)
    support_url = models.URLField(blank=True)

    fhir_reference = models.CharField(max_length=60,
                                      blank=True,
                                      null=True)

    # We should create/update a FHIR Device resource each time the Application record is
    # saved.

    # {
    #   "resourceType" : "Device",
    #   "identifier" : [{ Identifier }], // Client_Id
    #   "type" : { CodeableConcept }, // app_type
    #   "status" : "<code>", // available | not-available | entered-in-error
    #   "manufacturer" : "<string>", // Name of device manufacturer
    #   "model" : "<string>", // Model id assigned by the manufacturer
    #   "version" : "<string>", // Version number (i.e. software)
    #   "expiry" : "<dateTime>", // Date and time of expiry of this device (if applicable)

    #   "owner" : { Reference(Organization) }, // Organization responsible for device
    #   "location" : { Reference(Location) }, // Where the resource is found
    #   "contact" : [{ ContactPoint }], // Details for human/organization for support
    #   "url" : "<uri>" // Network address to contact device
    # }

    # on 201 Created write FHIR_reference using response header location field content
    # Otherwise use FHIR_Reference to update record on fhir server when application is updated

    def save(self, *args, **kwargs):

        if self.fhir_reference is "":
            if settings.DEBUG:
                print("Overriding BBApplication save")

            mode = "POST"
        else:
            mode = "PUT"
        self.fhir_reference = self.build_fhir(self, *args, **kwargs)

        super(BBApplication, self).save(*args, **kwargs)


    def build_fhir(self, *args, **kwargs):
        # Create a FHIR Device Record
        result = False

        if self.fhir_reference == "":
            mode = "POST"

        else:
            mode = "PUT"

        resource = OrderedDict()
        resource['resourceType'] = "Device"
        resource['identifier'] = [build_fhir_id("system", settings.DOMAIN,
                                  "type", {"text": "BBApplication"},
                                  "value", str(self.id))]
        resource['type'] = {"text": self.get_app_type_display()}
        if self.agree:
            resource['status'] = "available"
        else:
            resource['status'] = "not-available"
        resource['manufacturer'] = self.organization.name
        resource['model'] = self.name

        org = OrderedDict()
        org['resourceType'] = "Organization"

        id_info_1 = OrderedDict()
        id_info_1['system'] = settings.DOMAIN
        id_info_1['type'] = {"text": "Organization"}
        id_info_1['value'] = str(self.organization_id)


        org['identifier'] = [build_fhir_id("system", settings.DOMAIN,
                              "type", {"text": "Organization"},
                              "value", str(self.organization_id)),
                             build_fhir_id("system", "FHIR",
                              "type", {"text": "Developer Organization"},
                              "value", self.organization.fhir_reference)]
        resource['organization'] = org

        resource['url'] = self.support_url

        result = write_fhir(mode,
                            "Device",
                            json.dumps(resource),
                            self.fhir_reference)

        return result


    def privacy(self):
        return self.privacy_url

    def support(self):
        return self.support_url

    def terms_signed(self):
        if self.agree:
            terms = "Agreed to Terms and Conditions " \
                    "(v.%s) on %s" % (self.agree_version,self.agree_date)
            return terms
        return None

    def admin_list(self):
        return ('user', 'client_id', 'client_secret',)


class Organization(models.Model):
    # We need an Organization model to coordinate applications for a user
    # name and domain must be unique
    id = models.AutoField
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='+',
                              blank=True,
                              null=True,
                              verbose_name="Application Owner"
                              )
    name = models.CharField(max_length=100,
                            verbose_name='Organization Name',
                            unique=True)
    domain = models.URLField(unique=True)
    trusted = models.BooleanField(default=False)
    trusted_since = models.DateTimeField(blank=True, null=True)

    fhir_reference = models.CharField(max_length=60,
                                      blank=True,
                                      null=True)

    # We need to write an Organization Profile to FHIR and update FHIR_Reference
# {
#   "resourceType" : "Organization",
#   // from Resource: id, meta, implicitRules, and language
#   // from DomainResource: text, contained, extension, and modifierExtension
#   "identifier" : [{ Identifier }], // C? Identifies this organization  across multiple systems
#   "active" : <boolean>, // Whether the organization's record is still in active use
#   "type" : { CodeableConcept }, // Kind of organization
#   "name" : "<string>", // C? Name used for the organization
#   "telecom" : [{ ContactPoint }], // C? A contact detail for the organization
#   "address" : [{ Address }], // C? An address for the organization
#   "partOf" : { Reference(Organization) }, // The organization of which this organization forms a part
#   "contact" : [{ // Contact for the organization for a certain purpose
#     "purpose" : { CodeableConcept }, // The type of contact
#     "name" : { HumanName }, // A name associated with the contact
#     "telecom" : [{ ContactPoint }], // Contact details (telephone, email, etc.)  for a contact
#     "address" : { Address } // Visiting or postal addresses for the contact
#   }]
# }

    # On 201 Created write FHIR_reference using response header location field content
    # Otherwise use FHIR_Reference to update record on fhir server when application is updated


    def save(self, *args, **kwargs):

        if self.fhir_reference is "":
            if settings.DEBUG:
                print("Overriding Organization save")

            mode = "POST"
        else:
            mode = "PUT"
        self.fhir_reference = self.build_fhir(self, *args, **kwargs)

        super(Organization, self).save(*args, **kwargs)


    def build_fhir(self, *args, **kwargs):
        # Create a FHIR Organization Record
        result = False

        if self.fhir_reference == "":
            mode = "POST"

        else:
            mode = "PUT"

        resource = OrderedDict()
        resource['resourceType'] = "Organization"
        resource['identifier'] = [build_fhir_id("system", settings.DOMAIN,
                                  "type", {"text": "Organization"},
                                  "value", str(self.id))]
        resource['type'] = {"text": "Developer Organization"}
        resource['name'] = self.name
        telecom = OrderedDict()
        telecom['resourceType'] = "ContactPoint"
        telecom['system'] = "domain"
        telecom['value'] = self.domain
        resource['telecom'] = [telecom,]

        result = write_fhir(mode,
                            "Organization",
                            json.dumps(resource),
                            self.fhir_reference)

        return result

    def __str__(self):
        return self.name

    def url(self):
        return self.domain

    def trust(self):
        return self.trusted

    def owned_by(self):
        return self.owner.email


class Developer(models.Model):
    # Record Roles in an Organization

    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(settings.AUTH_USER_MODEL,
                               blank=True,
                               null=True)
    role = models.CharField(max_length=1,
                            choices=DEVELOPER_ROLE_CHOICES,
                            default='9')
    organization = models.ForeignKey(Organization,
                                     blank=True,
                                     null=True)

    def __str__(self):
        return ("[%s]%s(%s) for %s" % (self.id,
                                       self.member,
                                       self.role,
                                       self.organization))

    def primary(self):
        if self.role == "1":
            return True
        else:
            return False

    def id(self):
        return self.id

    def backup(self):
        if self.role == "2":
            return True
        else:
            return False

    def team_member(self):
        if self.role in  ['1', '2', '9']:
            return True
        else:
            return False

    def user_role(self):
        return self.role

    def linked_org(self):
        return self.organization

    def linked_user(self):
        User = settings.AUTH_USER_MODEL
        access_field = settings.USERNAME_FIELD
        if settings.DEBUG:
            print("Self:", self, "Developer:", self.member.__str__())
        try:
            u = User.objects.get(**{access_field:self.member})
            return "Changing this damn field name %s" % u.username
        except:
            return "No assigned member"


