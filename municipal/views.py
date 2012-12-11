# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from datetime import datetime

from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotAllowed

from authority.models import Term
from .models import Programme, ProgrammeItem
from .forms import ProgrammeHTitleForm, ProgrammeHDescriptionForm

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
            'in_future': delta.total_seconds() < SECONDS_PER_DAY / 2,
            'htitle_form': ProgrammeHTitleForm(self.object),
            'hdescription_form': ProgrammeHDescriptionForm(self.object)
        })

        # celkove hlasovani o bode
        out['total_voting'] = self.object.get_total_voting(out['voting'])
        return out

"""
TODO:
- zobecnit nejakou spolecnou tridu
- get by mohl namisto not allowed delat redirect na matersky detail
- musim doplnit generovani message
    - a najit pro ni v sablone nejake misto
- doladit podobu modalnich formularu
    - vetsi policka
    - vysvetlujici texty
    - poradi tlacitek
        - pokud je navrhnout az druhe, v pripade titulku se ENTER bere jako zavrit
    - focus na policko po otevreni modalu
- mohl bych to zajaxovat, bo vsecko se deje na te strance instantne...
- modalni okna v sablone generovat az nekde na konec...
"""

class ProgrammeHTitleView(CreateView):
    """
    Obsluha formulare, kterym lidi navrhuji srozumitelny titulek bodu programu.
    """
    form_class = ProgrammeHTitleForm

    def get_form_kwargs(self):
        out = super(ProgrammeHTitleView, self).get_form_kwargs()
        out.update({'item': self.item})
        return out

    def get_success_url(self):
        return self.item.get_absolute_url()

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed('Method Not Allowed')

    def post(self, request, *args, **kwargs):
        self.request = request
        self.item = self.get_object()
        return super(ProgrammeHTitleView, self).post(request, *args, **kwargs)

    def get_object(self):
        self.term = get_object_or_404(Term, valid_from__year=int(self.kwargs['year_from']), \
                                      valid_to__year=int(self.kwargs['year_to']))
        self.programme = get_object_or_404(Programme, term=self.term, \
                                           order=int(self.kwargs['programme']))
        item = get_object_or_404(ProgrammeItem, item=self.kwargs['item'], \
                                 programme=self.programme)
        return item


class ProgrammeHDescriptionView(CreateView):
    """
    Obsluha formulare, kterym lidi navrhuji obsah k bodu programu.
    """
    form_class = ProgrammeHDescriptionForm

    def get_form_kwargs(self):
        out = super(ProgrammeHDescriptionView, self).get_form_kwargs()
        out.update({'item': self.item})
        return out

    def get_success_url(self):
        return self.item.get_absolute_url()

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed('Method Not Allowed')

    def post(self, request, *args, **kwargs):
        self.request = request
        self.item = self.get_object()
        return super(ProgrammeHDescriptionView, self).post(request, *args, **kwargs)

    def get_object(self):
        self.term = get_object_or_404(Term, valid_from__year=int(self.kwargs['year_from']), \
                                      valid_to__year=int(self.kwargs['year_to']))
        self.programme = get_object_or_404(Programme, term=self.term, \
                                           order=int(self.kwargs['programme']))
        item = get_object_or_404(ProgrammeItem, item=self.kwargs['item'], \
                                 programme=self.programme)
        return item
