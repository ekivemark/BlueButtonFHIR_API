"""
 BBofUser: Account Framework top level

"""
from django.conf.urls import (include,
                              url)
from django.contrib import admin
from accounts import views
from accounts.views.user import (verify_phone, user_edit)
from accounts.views.other import (manage_account, logout, login)
from accounts.views.sms import (sms_code, sms_login)

admin.autodiscover()

# TODO: Implement Education Pages
# TODO: Replace Register Page with Education Page
# TODO: Add Link to Medicare Registration Page if User Not in LDAP

# DONE: Identify Modules that require accounts.session_master decorator
urlpatterns = [
                       # This is step 2 of login
                       url(r'^login$',
                           views.sms.sms_login,
                           name='login'),
                       # This is step one of login
                       url(r'smscode/',
                           views.sms.sms_code,
                           name='sms_code'),
                       url(r'^logout$',
                           views.logout,
                           name='logout'),
                       # Learn more...
                       url(r'^learn/0/$',
                           views.learn.learn_0,
                           name='learn_0'),
                       url(r'^learn/1/$',
                           views.learn.learn_1,
                           name='learn_1'),
                       url(r'^learn/2/$',
                           views.learn.learn_2,
                           name='learn_2'),

                       url(r'^register$',
                           views.other.register,
                           name='register'),
                       url(r'^$',
                           views.home_index,
                           name='home'),
                       # DONE: apply session_master
                       url(r'verify_phone',
                           views.user.verify_phone,
                           name='verify_phone'),
                        # DONE: apply session_master
                       url(r'^manage_account$',
                           views.other.manage_account,
                           name='manage_account'),
                       # DONE: apply session_master
                       url(r'^user/edit$',
                           views.user.user_edit,
                           name='user_edit'),
                       # DONE: apply session_master
                       url(r'^user/account_access$',
                           views.user.account_access,
                           name='account_access'),
                       # DONE: apply session_master

                       url(r'^admin/', include(admin.site.urls)),

                       # Manage Account
                       # Remove Account

                       ]
