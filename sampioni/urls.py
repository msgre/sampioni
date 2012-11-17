from django.conf.urls import patterns, include, url
from django.contrib import admin

from comments.views import HebloCommentDetailView, CommentDetailView

admin.autodiscover()

urlpatterns = patterns('',
    (r'^komentare/', include('comments.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
