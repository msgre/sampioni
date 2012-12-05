# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *

from events.views import AgendaListView, AgendaDetailView, AgendaItemDetailView

urlpatterns = patterns('',
    #url(r'^$', RepresentativeAgendaListView.as_view(), name="agenda-list"),
    url(r'^(?P<year_from>[0-9]{4})-(?P<year_to>[0-9]{4})/$', AgendaListView.as_view(), name="agenda-list"),
    url(r'^(?P<year_from>[0-9]{4})-(?P<year_to>[0-9]{4})/(?P<agenda>[\.0-9]+)/$', AgendaDetailView.as_view(), name="agenda-detail"),
    url(r'^(?P<year_from>[0-9]{4})-(?P<year_to>[0-9]{4})/(?P<agenda>[\.0-9]+)/(?P<item>[\.0-9]+)/$', AgendaItemDetailView.as_view(), name="agenda-item-detail"),
)
