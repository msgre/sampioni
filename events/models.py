# -*- coding: utf-8 -*-

"""
Dulezite udalosti.

Momentalne pouze bod jednani zastupitelstva. V budoucnu mozna i body z jednani
rady, prip. dalsi verejne vystupy mesta (napr. Forum 2025, apod).
"""

import math
from copy import deepcopy

from django.db import models
from django.utils.dateformat import DateFormat
from django.conf import settings
from django.utils.datastructures import SortedDict

from shared.utils import process_markdown, typotexy
from voting.models import RepresentativeVote


class RepresentativeAgenda(models.Model):
    """
    Jednani zastupitelstva.
    """
    TYPE_ORDINARY = 'R'
    TYPE_EXTRAORDINARY = 'M'
    TYPE_CHOICES = (
        (TYPE_ORDINARY, u'Řádné'),
        (TYPE_EXTRAORDINARY, u'Mimořádné'),
    )

    order   = models.IntegerField(u'Pořadové číslo')
    type    = models.CharField(u'Typ jednání', max_length=1, choices=TYPE_CHOICES, default=TYPE_ORDINARY)
    term    = models.ForeignKey("authority.Term", verbose_name=u"Volební období")
    date    = models.DateTimeField(u"Datum konání")
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Jednání zastupitelstva'
        verbose_name_plural = u'Jednání zastupitelstev'
        ordering = ('-term__valid_from', 'order')

    def __unicode__(self):
        return u'%s %s' % (self.order, self.get_type_display())

    @models.permalink
    def get_absolute_url(self):
        return ('agenda-detail', [], {'year_from': self.term.valid_from.year, \
                                      'year_to': self.term.valid_to.year, \
                                      'agenda': self.order})


REPRESENTATIVE_DEFAULTS = {
    'data': SortedDict([
        (RepresentativeVote.REPRESENTATIVE_VOTE_YES, {
            'icon': 'icon-thumbs-up',
            'label': RepresentativeVote.REPRESENTATIVE_VOTE_LABELS[RepresentativeVote.REPRESENTATIVE_VOTE_YES],
            'votes': 0,
            'votes_perc': 0,
            'representatives': []
        }),
        (RepresentativeVote.REPRESENTATIVE_VOTE_NO, {
            'icon': 'icon-thumbs-down',
            'label': RepresentativeVote.REPRESENTATIVE_VOTE_LABELS[RepresentativeVote.REPRESENTATIVE_VOTE_NO],
            'votes': 0,
            'votes_perc': 0,
            'representatives': []
        }),
        (RepresentativeVote.REPRESENTATIVE_VOTE_NOTHING, {
            'icon': 'icon-question-sign',
            'label': RepresentativeVote.REPRESENTATIVE_VOTE_LABELS[RepresentativeVote.REPRESENTATIVE_VOTE_NOTHING],
            'votes': 0,
            'votes_perc': 0,
            'representatives': []
        }),
        (RepresentativeVote.REPRESENTATIVE_VOTE_MISSING, {
            'icon': 'icon-remove-circle',
            'label': RepresentativeVote.REPRESENTATIVE_VOTE_LABELS[RepresentativeVote.REPRESENTATIVE_VOTE_MISSING],
            'votes': 0,
            'votes_perc': 0,
            'representatives': []
        })
    ])
}

class RepresentativeAgendaItem(models.Model):
    """
    Bod na jednani zastupitelstva.
    """
    AGENDA_RESULT_YES = '+'
    AGENDA_RESULT_NO  = '-'
    AGENDA_RESULT_CONFUSED = '?'
    AGENDA_RESULT_LABELS = {
        AGENDA_RESULT_YES: u'Schváleno',
        AGENDA_RESULT_NO: u'Neschváleno',
        AGENDA_RESULT_CONFUSED: u'Zmatečné',
    }
    AGENDA_RESULT_ICONS = {
        AGENDA_RESULT_YES: u'icon-thumbs-up',
        AGENDA_RESULT_NO: u'icon-thumbs-down',
        AGENDA_RESULT_CONFUSED: u'icon-question-sign',
    }
    AGENDA_RESULT_CHOICES = (
        (AGENDA_RESULT_YES, AGENDA_RESULT_LABELS[AGENDA_RESULT_YES]),
        (AGENDA_RESULT_NO, AGENDA_RESULT_LABELS[AGENDA_RESULT_NO]),
        (AGENDA_RESULT_CONFUSED, AGENDA_RESULT_LABELS[AGENDA_RESULT_CONFUSED]),
    )

    item             = models.CharField(u'Číslo bodu', max_length=10)
    title            = models.CharField(u'Titulek', max_length=2000)
    htitle           = models.CharField(u'Srozumitelný titulek', max_length=1000, blank=True, null=True)
    description_orig = models.TextField(u'Popis', blank=True, null=True)
    description      = models.TextField(editable=False, blank=True, null=True)
    agenda           = models.ForeignKey(RepresentativeAgenda, verbose_name=u"Jednání zastupitelstva", related_name='items')
    # denormalizace
    # TODO:
    #dvote            = models.CharField(editable=False, max_length=1, blank=True, null=True, choices=AGENDA_RESULT_CHOICES)
    created          = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated          = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Bod na jednání zastupitelstva'
        verbose_name_plural = u'Body z jednání zastupitelstva'
        ordering = ('item', ) # TODO: item musim denormalizovat do cisla, klidne decimalu, a radit pak podle nej trebas

    def __unicode__(self):
        return u'%s %s' % (self.agenda, self.item)

    @models.permalink
    def get_absolute_url(self):
        term = self.agenda.term
        return ('agenda-item-detail', [], {'year_from': term.valid_from.year, \
                                           'year_to': term.valid_to.year, \
                                           'agenda': self.agenda.order, \
                                           'item': self.item})

    def save(self, *args, **kwargs):
        self.description = typotexy(process_markdown(self.description_orig))
        return super(RepresentativeAgendaItem, self).save(*args, **kwargs)

    def get_voting_data(self):
        """
        Vrati SortedDict s prubehem hlasovani.
        """
        out = SortedDict()
        # rozprcani zastupitelu do slovniku
        for voting in self.voting.all().order_by('order'):
            counter = 0
            _item = deepcopy(REPRESENTATIVE_DEFAULTS)
            for rvote in voting.rvote.all().order_by('representative__politician__last_name'):
                _item['data'][rvote.vote]['representatives'].append(rvote.representative)
                _item['data'][rvote.vote]['votes'] += 1
                counter += 1

            if counter == 0:
                continue
            _item['confused'] = voting.confused
            _item['description'] = voting.description
            _item['order'] = voting.order

            # vypocet procent
            for k in _item['data']:
                _item['data'][k]['votes_perc'] = 100 * _item['data'][k]['votes'] / float(counter)

            out[voting.order] = _item

        return out

    def get_total_voting(self, voting):
        """
        Celkovy verdikt hlasovani.
        """
        if not voting:
            return None

        out = {'data': {}}
        for order in voting:
            if not voting[order] or not voting[order]['data']:
                continue
            item = voting[order]['data']

            total = sum([item[k]['votes'] for k in item])
            limit = int(math.ceil(total / 2.0))
            win = [k for k in item if item[k]['votes'] >= limit]
            if voting[order]['confused']:
                result = self.AGENDA_RESULT_CONFUSED
            elif win and win[0] == RepresentativeVote.REPRESENTATIVE_VOTE_YES:
                result = self.AGENDA_RESULT_YES
            else:
                result = self.AGENDA_RESULT_NO

            out['data'][order] = {'result': result,
                                  'result_bool': result == self.AGENDA_RESULT_YES,
                                  'limit': limit,
                                  'total': total,
                                  'tightly': result==self.AGENDA_RESULT_YES and item[win[0]]['votes'] <= limit + 2,
                                  'icon': self.AGENDA_RESULT_ICONS[result],
                                  'label': self.AGENDA_RESULT_LABELS[result],
                                  'confused': voting[order]['confused'],
                                  'description': voting[order]['description'],
                                  'order': voting[order]['order']}

        # doplnime statisticke udaje o celkovych vysledcich
        out['confused_count'] = len([1 for k in out['data'] if out['data'][k]['confused']])
        out['total_count'] = len(out['data'])
        out['valid_count'] = out['total_count'] - out['confused_count']
        out['multiple_icon'] = 'icon-reorder'

        return out
