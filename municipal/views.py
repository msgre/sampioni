# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from datetime import datetime

from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from authority.models import Term
from .models import Programme, ProgrammeItem

SECONDS_PER_DAY = 60 * 60 * 24


class ProgrammeListView(ListView):
    """
    Prehled programu jednani na zastupitelstvu v danem volebnim obdobi.
    """
    context_object_name = 'programmes'
    template_name = 'municipal/programme_list.html'

    def get_queryset(self):
        return Programme.objects.all()

    def get_context_data(self, **kwargs):
        out = super(ProgrammeListView, self).get_context_data(**kwargs)
        out.update({
            'url_year_from': self.kwargs['year_from'],
            'url_year_to': self.kwargs['year_to'],
        })
        return out


class ProgrammeDetailView(DetailView):
    """
    Detail programu jednani na zastupitelstvu.
    """
    context_object_name = 'programme'
    template_name = 'municipal/programme_detail.html'

    def get_queryset(self):
        self.term = get_object_or_404(Term, valid_from__year=int(self.kwargs['year_from']), \
                                 valid_to__year=int(self.kwargs['year_to']))
        programme = get_object_or_404(Programme, term=self.term)
        return programme

    def get_context_data(self, **kwargs):
        out = super(ProgrammeDetailView, self).get_context_data(**kwargs)
        out.update({
            'term': self.term,
            'url_year_from': self.kwargs['year_from'],
            'url_year_to': self.kwargs['year_to'],
            'url_programme': self.kwargs['programme'],
        })
        return out


class ProgrammeItemDetailView(DetailView):
    """
    Detail konkretniho bodu programu projednavaneho na zastupitelstvu.
    """
    context_object_name = 'programme_item'
    template_name = 'municipal/programme_item_detail.html'

    def get_object(self, queryset=None):
        self.term = get_object_or_404(Term, valid_from__year=int(self.kwargs['year_from']), \
                                      valid_to__year=int(self.kwargs['year_to']))
        self.programme = get_object_or_404(Programme, term=self.term, \
                                           order=int(self.kwargs['programme']))
        item = get_object_or_404(ProgrammeItem, item=self.kwargs['item'], \
                                 programme=self.programme)
        return item

    def get_context_data(self, **kwargs):
        out = super(ProgrammeItemDetailView, self).get_context_data(**kwargs)
        delta = datetime.now() - self.object.programme.date
        out.update({
            'term': self.term,
            'programme': self.programme,
            'url_year_from': self.kwargs['year_from'],
            'url_year_to': self.kwargs['year_to'],
            'url_programme': self.kwargs['programme'],
            'url_item': self.kwargs['item'],
            'voting': self.object.get_voting_data(),
            'deep_history': delta.total_seconds() > SECONDS_PER_DAY * 10,
            'in_future': delta.total_seconds() < SECONDS_PER_DAY / 2
        })

        # celkove hlasovani o bode
        out['total_voting'] = self.object.get_total_voting(out['voting'])
        return out
