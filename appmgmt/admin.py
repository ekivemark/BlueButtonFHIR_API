from django import forms
from django.contrib import admin

# Register your models here.

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from appmgmt.models import (BBApplication,
                            Organization,
                            Developer,
                            )

from oauth2_provider.models import get_application_model
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


Application = get_application_model()


admin.site.register(Organization, OrganizationAdmin)

# BBApplication is already registered via oauth2_provider and settings.py
# So we have to unregister and reregister to voerride the default admin_disable view applied
# in oauth2_provider (RawIDAdmin) which just defines 'user' for list view

admin.site.unregister(Application)
admin.site.register(Application, BBApplicationAdmin)
admin.site.register(Developer, DeveloperAdmin)
