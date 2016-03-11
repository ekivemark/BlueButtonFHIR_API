# apps.v1api.admin

# Register your models here.


from django import forms
from django.contrib import admin

from django.conf import settings

from .models import Crosswalk

class CrosswalkAdmin(admin.ModelAdmin):
    """
    Admin form for Crosswalk model
    """

    list_display = ('user', 'guid', 'fhir_url_id', 'fhir')
    readonly_fields = ('date_created', 'guid')


admin.site.register(Crosswalk, CrosswalkAdmin)

