from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from comments.views import HebloCommentDetailView, CommentDetailView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^zastupitelstvo/', include('events.urls')),

    (r'^komentare/', include('comments.urls')),
    (r'^$', TemplateView.as_view(template_name="homepage.html")),
    (r'^faq/$', TemplateView.as_view(template_name="faq.html")),
    # testy
    (r'^volebni-obdobi/$', TemplateView.as_view(template_name="comments/volebni_obdobi.html")),
    (r'^volebni-obdobi/2010-2014/$', TemplateView.as_view(template_name="comments/volebni_obdobi_2010.html")),
    (r'^pridat/$', TemplateView.as_view(template_name="comments/pridat.html")),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
