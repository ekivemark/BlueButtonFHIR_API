"""
 BBofUser: Account Framework top level

"""
from django.conf.urls import (patterns,
                              include,
                              url)
from django.contrib import admin

from accounts.views.user import (verify_phone, user_edit)
from accounts.views.other import (manage_account, logout, login)
from accounts.views.sms import (sms_code, sms_login)

admin.autodiscover()

# TODO: Implement Education Pages
# TODO: Replace Register Page with Education Page
# TODO: Add Link to Medicare Registration Page if User Not in LDAP

# DONE: Identify Modules that require accounts.session_master decorator
urlpatterns = patterns('',
                       # This is step 2 of login
                       url(r'^login$',
                           'accounts.views.sms.sms_login',
                           name='login'),
                       # This is step one of login
                       url(r'smscode/',
                           'accounts.views.sms.sms_code',
                           name='sms_code'),
                       url(r'^logout$',
                           'accounts.views.logout',
                           name='logout'),
                       # Learn more...
                       url(r'^learn/0/$',
                           'accounts.views.learn.learn_0',
                           name='learn_0'),
                       url(r'^learn/1/$',
                           'accounts.views.learn.learn_1',
                           name='learn_1'),
                       url(r'^learn/2/$',
                           'accounts.views.learn.learn_2',
                           name='learn_2'),

                       url(r'^register$',
                           'accounts.views.other.register',
                           name='register'),
                       url(r'^$',
                           'accounts.views.home_index',
                           name='home'),
                       # DONE: apply session_master
                       url(r'verify_phone',
                           'accounts.views.user.verify_phone',
                           name='verify_phone'),
                        # DONE: apply session_master
                       url(r'^manage_account$',
                           'accounts.views.other.manage_account',
                           name='manage_account'),
                       # DONE: apply session_master
                       url(r'^user/edit$',
                           'accounts.views.user.user_edit',
                           name='user_edit'),
                       # DONE: apply session_master
                       url(r'^user/account_access$',
                           'accounts.views.user.account_access',
                           name='account_access'),
                       # DONE: apply session_master

                       url(r'^admin/', include(admin.site.urls)),

                       # Manage Account
                       # Remove Account

                       )
