from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

# Register your models here.

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from appmgmt.models import (BBApplication,
                            Organization,
                            Developer,
                            )

from oauth2_provider.models import (get_application_model,
                                    Grant,
                                    AccessToken,
                                    RefreshToken)

from oauth2_provider.settings import oauth2_settings


# class BBApplicationCreationForm(forms.ModelForm):
#     """
#     BBApplication Creation Form
#     """
#
#
#     class Meta:
#         model = BBApplication
#         fields = ('logo', 'agree')
#
#
# class BBApplicationUpdateForm(forms.ModelForm):
#     """
#     BBApplication Update Form
#     """
#
#     class Meta:
#         model = BBApplication
#         fields = ('logo', 'agree')

class BBApplicationAdmin(admin.ModelAdmin):
    """

    """
    # model = BBApplication
    list_display = ('name', 'owner',
                    'client_id', 'client_secret',
                    'client_type', 'authorization_grant_type' )


class OrganizationAdmin(admin.ModelAdmin):
    """
    Tailor the Organization page in the Admin module
    """
    # DONE: Add Admin view for Organizations
    list_display = ('name', 'owner', 'domain')

    def save_model(self, request, obj, form, change):
        """
        When creating a new object, set the creator field.
        """
        if settings.DEBUG:
            print("Saving model with ", request.user)
            print("mode=", change)
        if not change:
            obj.owner = request.user

        obj.save()


class DeveloperAdmin(admin.ModelAdmin):
    """

    """
    model = Developer

    list_display = ('id', 'member', 'linked_user', 'role', 'organization' )


class DeveloperCreationForm(forms.ModelForm):
    class Meta:
        model = Developer
        fields = ( 'role', 'organization')


class DeveloperUpdateForm(forms.ModelForm):
    """
    Developer Update Form
    """

    class Meta:
        model = Developer

        fields = ('role', 'organization')


class GrantAdmin(admin.ModelAdmin):
    """
    Overide Oauth2_provider Grants Admin to add extra fields to display and search
    """
    list_display = ('code', 'user', 'application', 'redirect_uri')

    search_fields = ('code', 'user__username', 'application__name')

    # user = models.ForeignKey(AUTH_USER_MODEL)
    # code = models.CharField(max_length=255, db_index=True)  # code comes from oauthlib
    # application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL)
    # expires = models.DateTimeField()
    # redirect_uri = models.CharField(max_length=255)
    # scope = models.TextField(blank=True)


class AccessTokenAdmin(admin.ModelAdmin):
    """
    Overide OAuth2_provier AccessToken Admin to add extra fields to display and search
    """

    list_display = ('token', 'user', 'application', 'expires')

    search_fields = ('token', 'user__username', 'application__name')

    # user = models.ForeignKey(AUTH_USER_MODEL, blank=True, null=True)
    # token = models.CharField(max_length=255, db_index=True)
    # application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL)
    # expires = models.DateTimeField()
    # scope = models.TextField(blank=True)

class RefreshTokenAdmin(admin.ModelAdmin):
    """
    Overide OAuth2_provier RefreshToken Admin to add extra fields to display and search
    """


    list_display = ('token', 'user', 'application', 'access_token')

    search_fields = ('token', 'user__username', 'application__name', 'access_token__token')

    # user = models.ForeignKey(AUTH_USER_MODEL)
    # token = models.CharField(max_length=255, db_index=True)
    # application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL)
    # access_token = models.OneToOneField(AccessToken,
    #                                     related_name='refresh_token')



Application = get_application_model()


admin.site.register(Organization, OrganizationAdmin)

# BBApplication is already registered via oauth2_provider and settings.py
# So we have to unregister and reregister to override the default admin view applied
# in oauth2_provider (RawIDAdmin) which just defines 'user' for list view

admin.site.unregister(Application)
admin.site.register(Application, BBApplicationAdmin)
admin.site.register(Developer, DeveloperAdmin)
admin.site.unregister(Grant)
admin.site.register(Grant, GrantAdmin)
admin.site.unregister(AccessToken)
admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.unregister(RefreshToken)
admin.site.register(RefreshToken, RefreshTokenAdmin)