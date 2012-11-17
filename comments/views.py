# -*- coding: utf-8 -*-

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import Site

from .models import Comment


class CommentDetailView(DetailView):
    """
    Uplny, kompletni detail komentare.
    """
    context_object_name = 'comment'
    template_name = 'comments/comment_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        out = super(CommentDetailView, self).get_context_data(**kwargs)
        out.update()
        return out


class HebloCommentDetailView(DetailView):
    """
    Zkracena forma detailu komentare urcena pro heblo.
    """
    context_object_name = 'comment'
    template_name = 'comments/heblo_comment_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        out = super(HebloCommentDetailView, self).get_context_data(**kwargs)
        out.update({'site': Site.objects.get_current()})
        return out
