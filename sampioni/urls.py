from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from municipal.views import APITermList, APITermDetail, \
                            APIProgrammeList, APIProgrammeDetail, \
                            APIProgrammeItemList, APIProgrammeItemDetail

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^zastupitelstvo/', include('municipal.urls')),

    # (r'^komentare/', include('comments.urls')),
    # (r'^$', TemplateView.as_view(template_name="homepage.html")),
    # (r'^faq/$', TemplateView.as_view(template_name="faq.html")),
    # # testy
    # (r'^volebni-obdobi/$', TemplateView.as_view(template_name="comments/volebni_obdobi.html")),
    # (r'^volebni-obdobi/2010-2014/$', TemplateView.as_view(template_name="comments/volebni_obdobi_2010.html")),
    # (r'^pridat/$', TemplateView.as_view(template_name="comments/pridat.html")),

    # TODO: docasne, zkusam api
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/term/$', APITermList.as_view(), name="api-term-list"),
    url(r'^api/term/(?P<term>\d+)/$', APITermDetail.as_view(), name="api-term-detail"),
    url(r'^api/term/(?P<term>\d+)/programme/$', APIProgrammeList.as_view(), name="api-programme-list"),
    url(r'^api/term/(?P<term>\d+)/programme/(?P<programme>\d+)/$', APIProgrammeDetail.as_view(), name="api-programme-detail"),
    url(r'^api/term/(?P<term>\d+)/programme/(?P<programme>\d+)/items/$', APIProgrammeItemList.as_view(), name="api-programmeitem-list"),
    url(r'^api/term/(?P<term>\d+)/programme/(?P<programme>\d+)/items/(?P<item>\d+)/$', APIProgrammeItemDetail.as_view(), name="api-programmeitem-detail"),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
