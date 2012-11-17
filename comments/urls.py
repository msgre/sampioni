# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import HebloCommentDetailView, CommentDetailView

urlpatterns = patterns('',
    url(r'^(?P<slug>[\-\_A-Za-z0-9]+)/heblo/$', HebloCommentDetailView.as_view(), name="heblo-comment-detail"),
    url(r'^(?P<slug>[\-\_A-Za-z0-9]+)/$', CommentDetailView.as_view(), name="comment-detail"),
)
