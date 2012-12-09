# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from datetime import datetime

from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from authority.models import Term
from .models import RepresentativeAgenda, RepresentativeAgendaItem

SECONDS_PER_DAY = 60 * 60 * 24


class AgendaListView(ListView):
    """
    Prehled jednani na zastupitelstvu v danem volebnim obdobi.
    """
    context_object_name = 'agendas'
    template_name = 'events/agenda_list.html'

    def get_queryset(self):
        return RepresentativeAgenda.objects.all()

    def get_context_data(self, **kwargs):
        out = super(AgendaListView, self).get_context_data(**kwargs)
        out.update({
            'url_year_from': self.kwargs['year_from'],
            'url_year_to': self.kwargs['year_to'],
        })
        return out


class AgendaDetailView(DetailView):
    """
    Detail jednani na zastupitelstvu.
    """
    context_object_name = 'agenda'
    template_name = 'events/agenda_detail.html'

    def get_queryset(self):
        self.term = get_object_or_404(Term, valid_from__year=int(self.kwargs['year_from']), \
                                 valid_to__year=int(self.kwargs['year_to']))
        agenda = get_object_or_404(RepresentativeAgenda, term=self.term)
        return agenda

    def get_context_data(self, **kwargs):
        out = super(AgendaDetailView, self).get_context_data(**kwargs)
        out.update({
            'term': self.term,
            'url_year_from': self.kwargs['year_from'],
            'url_year_to': self.kwargs['year_to'],
            'url_agenda': self.kwargs['agenda'],
        })
        return out


class AgendaItemDetailView(DetailView):
    """
    Detail konkretniho bodu projednavaneho na zastupitelstvu.
    """
    context_object_name = 'agenda_item'
    template_name = 'events/agenda_item_detail.html'

    def get_object(self, queryset=None):
        self.term = get_object_or_404(Term, valid_from__year=int(self.kwargs['year_from']), \
                                      valid_to__year=int(self.kwargs['year_to']))
        self.agenda = get_object_or_404(RepresentativeAgenda, term=self.term, \
                                        order=int(self.kwargs['agenda']))
        item = get_object_or_404(RepresentativeAgendaItem, item=self.kwargs['item'], \
                                 agenda=self.agenda)
        return item

    def get_context_data(self, **kwargs):
        out = super(AgendaItemDetailView, self).get_context_data(**kwargs)
        delta = datetime.now() - self.object.agenda.date
        out.update({
            'term': self.term,
            'agenda': self.agenda,
            'url_year_from': self.kwargs['year_from'],
            'url_year_to': self.kwargs['year_to'],
            'url_agenda': self.kwargs['agenda'],
            'url_item': self.kwargs['item'],
            'voting': self.object.get_voting_data(),
            'deep_history': delta.total_seconds() > SECONDS_PER_DAY * 10,
            'in_future': delta.total_seconds() < SECONDS_PER_DAY / 2
        })

        # celkove hlasovani o bode
        out['total_voting'] = self.object.get_total_voting(out['voting'])
        return out
