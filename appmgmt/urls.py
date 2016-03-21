# -*- coding: utf-8 -*-
"""
bofhirdev
FILE: urls
Created: 10/29/15 8:04 AM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.conf.urls import include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView

from appmgmt.models import BBApplication

from appmgmt.views import(main)
from appmgmt.views.application import (MyApplicationListView,
                                       MyApplicationUpdateView,
                                       MyApplicationCreate,
                                       Application_Update_Secret,
                                       Manage_Applications,
                                       MyApplicationDetailView,
                                       MyApplicationDeleteView,
                                       My_Application_Update)
from appmgmt.views.main import (home_index)

from appmgmt.views.organization import (MyOrganizationListView,
                                        MyOrganizationUpdateView,
                                        My_Organization_Create,
                                       )

from appmgmt.views.developer import (DeveloperList,
                                     DeveloperCreate,
                                     UserDomainList,
                                     DevTeam_Role_Change,
                                     DevTeam_Add,
                                     DevTeam_Delete)

from appmgmt.views.trust import (TrustData,
                                 BaseTrust,
                                 TrustTest,
                                 )

from appmgmt.views.poet import CallBack

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
                       # Examples:
                       # url(r'^$', 'bofhirdev.views.home', name='home'),

                       url(r'^$', main.home_index,
                           name='home'),
# Intro
                       url(r'^intro/$',
                           TemplateView.as_view(template_name='appmgmt/developer_intro.html'),
                           name="developer_intro"),
# Organization
                       url(r'^myorganizations/$',
                           MyOrganizationListView.as_view(),
                           name='organization_view'),
                       url(r'^createorganization/$',
                           My_Organization_Create,
                           name='organization_create'),
                       url(r'^updateorganization/(?P<pk>[0-9]+)/$',
                           MyOrganizationUpdateView.as_view(success_url=reverse_lazy('accounts:manage_account')),
                           name='organization_update'),
# Developer
                       url(r'^developers/$', DeveloperList.as_view(),
                           name='developer_view'),
                       url(r'^developer_add/$',
                           DeveloperCreate.as_view(success_url=reverse_lazy('appmgmt:developer_view')),
                           name='developer_create'),
                       url(r'^domain_users/$', UserDomainList.as_view(),
                           name='domain_user_view'),
# DevTeam
                       url(r'^devteam/add/(?P<pk>[0-9]+)/$',
                           DevTeam_Add,
                           name='devteam_add'),
                       url(r'^devteam/delete/(?P<pk>[0-9]+)/$',
                           DevTeam_Delete,
                           name='devteam_delete'),
                       url(r'^devteam/edit/(?P<pk>[0-9]+)/$',
                           DevTeam_Role_Change,
                           name='devteam_role_change'),
# Applications
                       url(r'^myapplications/$',
                           Manage_Applications,
                           name='manage_applications'),
                       url(r'^createapplication/$',
                           MyApplicationCreate.as_view(success_url=reverse_lazy('appmgmt:manage_applications')),
                           name='application_create'),
                       url(r'^updateapplication/(?P<pk>[0-9]+)/$',
                           My_Application_Update,
                           name='application_update'),

                       url(r'^updateapplicationsecret/(?P<pk>[0-9]+)/$',
                           Application_Update_Secret,
                           name='application_update_secret'),
                       url(r'^viewapplication/(?P<pk>[0-9]+)/$',
                           MyApplicationDetailView.as_view(),
                           name='application_view'),

                       url(r'^deleteapplication/(?P<pk>[\w]+)/$',
                           MyApplicationDeleteView.as_view(model=BBApplication,
                                                           success_url=reverse_lazy('appmgmt:manage_applications'),
                                                           template_name='appmgmt/bbapplication_delete.html',
                                                           success_message='Your Application has been deleted successfully.'),
                           name='application_delete'),

# trust
                       url(r'^trustdata/$', TrustData,
                           name='trustdata'),
                       url(r'^trustcheck/(?P<requester_email>.+)/(?P<bundle>.+)/(?P<domain>.+)/(?P<owner_email>.+)$',
                           BaseTrust,
                           name='trustcheck'),
                       url(r'^trust_test/$',
                           TrustTest,
                           name='trusttest'),
                       url(r'^poet_callback/$',
                           CallBack,
                           name='post_callback'),
                       ]
