from django.conf import *
from registration.backends.default.urls import *
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy

# from accounts.forms.other import RegistrationFormUserTOSAndEmail
# from apps.secretqa.views import *
# from apps.subacc.views import *
from apps.api.views import *
from apps.home.views import WhatIsNewListView

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'bbonfhiruser.views.home', name='home'),
                       url(r'^$', 'apps.home.views.home_index',
                           name='home'),
                       # url(r'^about/$', 'apps.home.views.about',
                       #     name='about'),
                       url(r'^base/',
                           include('apps.home.urls', namespace='base')),

                       # url(r'^whatsnew/$', WhatIsNewListView.as_view(),
                       #     name='whatsnew'),
                       url(r'^accounts/',
                           include('accounts.urls', namespace='accounts')),
                       url(r'^appmanagement/',
                           include('appmgmt.urls', namespace='appmgmt')),

                       # url(r'^upload/', include('apps.uploader.urls',
                       #                          namespace='upload')),
                       # url(r'^subaccount/',
                       #     include('apps.subacc.urls', namespace='subaccount')),
                       # url(r'^security/',
                       #     include('apps.secretqa.urls', namespace='security')),
                       # API Entry point
                       # v1api is referenced inside apps.api.urls as v1
                       url(r'^api/',
                           include('apps.api.urls', namespace='api')),
                       # url(r'^npi_up/', include('apps.npi_upload.urls',
                       #                          namespace='npi_upload')),
                       # url(r'^getbb/', include('apps.getbb.urls',
                       #                         namespace='getbb')),
                       # url(r'^eob_upload/', include('apps.eob_upload.urls',
                       #                         namespace='eob_upload')),

                       # Registration Options:
                       # 1. Developer
                       # 2. Beneficiary - Not Authenticated
                       # 3. Beneficiary - Authenticated but not activated
                       url(r'^registration/register/$',
                           RegistrationView.as_view(),
                           name='register'),
                       # url(r'^logout$',
                       #     'accounts.views.logout',
                       #     name='logout'),
                       url(r'^registration/', include(
                           'registration.backends.default.urls', )),
                       url(r'^password/reset/$', auth_views.password_reset,
                           {'post_reset_redirect': reverse_lazy(
                               'password_reset_done')},
                           name='password_reset'),
                       url(
                           r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
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
                       url(r'^o/', include('oauth2_provider.urls',
                                           namespace='oauth2_provider')),

                       # OAuth2 Provider Library
                       url(r'^o/', include('oauth2_provider.urls',
                                           namespace='oauth2_provider')),
                       url(r'^admin/', include(admin.site.urls)),
                       # Uncomment the admin/doc line below to enable admin
                       # documentation:
                       url(r'^admin/doc/',
                           include('django.contrib.admindocs.urls')),
                       )
