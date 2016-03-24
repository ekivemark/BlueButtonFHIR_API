
from registration.backends.default.urls import *
from django.contrib import admin

# Add next two lines to display static and media files
# then add +static statement at the end of the urlpatterns
from django.conf import *
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy

from django.views.generic import TemplateView
from django.views.static import serve as Static_Serve

from accounts.forms.other import (RegistrationFormUserTOSAndEmail,
                                  RegistrationFormDeveloperTOSAndEmail)

from apps.api.views import *
from apps.home.views import WhatIsNewListView, versionView

from apps.home import views

from django.contrib import admin

admin.autodiscover()

urlpatterns = [
                       # url(r'^$', 'bbonfhiruser.views.home', name='home'),
                       url(r'^$', views.home_index ,
                           name='home'),
                       # url(r'^about/$', views.about,
                       #     name='about'),
                       url(r'^base/',
                           include('apps.home.urls', namespace='base')),
                       url(r'^version/$', views.versionView,
                           name="versionview"),

                       # url(r'^whatsnew/$', WhatIsNewListView.as_view(),
                       #     name='whatsnew'),
# Accounts
                       url(r'^accounts/',
                           include('accounts.urls', namespace='accounts')),
# AppMgmt
                       url(r'^appmanagement/',
                           include('appmgmt.urls', namespace='appmgmt')),

                       # API Entry point
                       # v1api is referenced inside apps.api.urls as v1
# api
                       url(r'^api/',
                           include('apps.api.urls', namespace='api')),

# registration
                       # Registration Options:
                       # 1. Developer
                       # 2. Beneficiary - Not Authenticated
                       # 3. Beneficiary - Authenticated but not activated
                       url(r'^registration/register/$',
                           RegistrationView.as_view(form_class=RegistrationFormUserTOSAndEmail),
                           name='register'),
                       url(r'^registration/registerdeveloper/$',
                           RegistrationView.as_view(form_class=RegistrationFormDeveloperTOSAndEmail),
                           name='register_developer'),
                       url(r'^registration/', include(
                           'registration.backends.default.urls', )),

                       url(r'^auto_registration/',
                           include('registration.backends.simple.urls')),

# password
                       url(r'^password/reset/$', auth_views.password_reset,
                           {'post_reset_redirect': reverse_lazy(
                               'password_reset_done')},
                           name='password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
                           auth_views.password_reset_confirm,
                           name='password_reset_confirm'),
                       url(r'^password/reset/complete/$',
                           auth_views.password_reset_complete,
                           {'post_reset_redirect': reverse_lazy(
                               'password_reset_complete')},
                           name='password_reset_complete'),
                       url(r'^password/reset/done/$',
                           auth_views.password_reset_done,
                           name='password_reset_done'),
# fhir
                       url(r'^fhir/', include('fhir.urls',
                                              namespace='fhir')),
# OAuth2_provider
                       url(r'^o/', include('oauth2_provider.urls',
                                           namespace='oauth2_provider')),

                       # OAuth2 Provider Library
                       url(r'^o/', include('oauth2_provider.urls',
                                           namespace='oauth2_provider')),
# Templates
                       url(r'^support/$', TemplateView.as_view(template_name='support.html')),

# Setup
                       url(r'^setup/', include('apps.setup.urls',
                                                namespace='setup')),

# Admin
                       url(r'^admin/', include(admin.site.urls)),
                       # Uncomment the admin_disable/doc line below to enable admin_disable
                       # documentation:
                       url(r'^admin/doc/',
                           include('django.contrib.admindocs.urls')),

                       ]#  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Django 1.8 method for serving static media files
if settings.DEBUG:
    urlpatterns.append(url(r'^media/(?P<path>.*)$',
                         Static_Serve,
                         {'document_root': settings.MEDIA_ROOT}))