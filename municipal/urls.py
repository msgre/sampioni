# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *

from .views import ProgrammeListView, ProgrammeDetailView, ProgrammeItemDetailView

urlpatterns = patterns('',
    #url(r'^$', RepresentativeProgrammeListView.as_view(), name="programme-list"),
    url(r'^(?P<year_from>[0-9]{4})-(?P<year_to>[0-9]{4})/$', ProgrammeListView.as_view(), name="programme-list"),
    url(r'^(?P<year_from>[0-9]{4})-(?P<year_to>[0-9]{4})/(?P<programme>[\.0-9]+)/$', ProgrammeDetailView.as_view(), name="programme-detail"),
    url(r'^(?P<year_from>[0-9]{4})-(?P<year_to>[0-9]{4})/(?P<programme>[\.0-9]+)/(?P<item>[\.0-9]+)/$', ProgrammeItemDetailView.as_view(), name="programme-item-detail"),
)
