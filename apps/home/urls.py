# -*- coding: utf-8 -*-
"""
BlueButtonFHIR_API
FILE: home.urls
Created: 12/15/15 9:50 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.conf.urls import (patterns,
                              include,
                              url)
from django.core.urlresolvers import reverse_lazy
from django.contrib import admin

from apps.home.views import (WhatIsNewListView,
                             WhatIsNewDetailView,
                             WhatIsNewUpdateView,
                             WhatIsNewDeleteView)


from .views import (what_is_new_create, )

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', WhatIsNewListView.as_view(),
                           name="new_stuff"),
                       url(r'^create/$',
                           what_is_new_create.as_view(success_url=reverse_lazy('base:new_stuff')),
                           name='new_stuff_create'),
                       url(r'^update/(?P<pk>\d+)/$',
                           WhatIsNewUpdateView.as_view(success_url=reverse_lazy('base:new_stuff')),
                           name='new_stuff_update'),
                       url(r'^item/(?P<pk>\d+)/$',
                           WhatIsNewDetailView.as_view(),
                           name="newsitem"),
                       url(r'^delete/(?P<pk>\d+)/$',
                           WhatIsNewDeleteView.as_view(success_url=reverse_lazy('base:new_stuff')),
                           name="new_stuff_delete"),
                       )

