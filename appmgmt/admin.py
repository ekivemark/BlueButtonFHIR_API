from django import forms
from django.contrib import admin

# Register your models here.

from django.conf import settings
from appmgmt.models import (BBApplication,
                            Organization,
                            Developer,
                            )


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
    list_display = ('name','organization', 'owner',
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

# admin.site.register(Account)

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(BBApplication, BBApplicationAdmin)
admin.site.register(Developer, DeveloperAdmin)
