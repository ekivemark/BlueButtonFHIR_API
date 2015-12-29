# Create your models here.
# apps.appmgmt.models

# Extend the Django OAuth Provider Application Model
# Author: Mark Scrimshire (c) @ekivemark

from django.conf import settings
from django.db import models
from oauth2_provider.models import AbstractApplication

# 1 = Top level account access
# 2 = Backup level account access
# 9 or Standard Team member access
DEVELOPER_ROLE_CHOICES = (('1', 'Account Owner'),
                          ('2', 'Backup Owner'),
                          ('9', 'Team Member'),
                          ('-', 'None' ),
                         )


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
    privacy_url = models.URLField(blank=True)
    support_url = models.URLField(blank=True)

    def privacy(self):
        return self.privacy_url

    def support(self):
        return self.support_url

    def terms_signed(self):
        if self.agree:
            terms = "Agreed to Terms and Conditions (v.%s) on %s" % (self.agree_version,
                                                                     self.agree_date)
            return terms
        return None


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
    trusted_until = models.DateTimeField(blank=True, null=True)

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