# -*- coding: utf-8 -*-

"""
TODO:
"""

import re
import math
from copy import deepcopy

from django.db import models
from django.utils.dateformat import DateFormat
from django.conf import settings
from django.utils.datastructures import SortedDict

from shared.utils import process_markdown, typotexy, replace_multiple_whitechars
from voting.models import RepresentativeVote


# --- program -----------------------------------------------------------------

class Programme(models.Model):
    """
    Program jednani zastupitelstva.
    """
    TYPE_ORDINARY = 'R'
    TYPE_EXTRAORDINARY = 'M'
    TYPE_CHOICES = (
        (TYPE_ORDINARY, u'Řádné'),
        (TYPE_EXTRAORDINARY, u'Mimořádné'),
    )
    # TODO: stazen, pridan, verejne hlasovani

    order   = models.IntegerField(u'Pořadové číslo')
    type    = models.CharField(u'Typ jednání', max_length=1, choices=TYPE_CHOICES, default=TYPE_ORDINARY)
    term    = models.ForeignKey("authority.Term", verbose_name=u"Volební období")
    date    = models.DateTimeField(u"Datum konání")
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Program jednání zastupitelstva'
        verbose_name_plural = u'Program jednání zastupitelstev'
        ordering = ('-term__valid_from', 'order')

    def __unicode__(self):
        return u'%s. %s, %s' % (self.order, self.get_type_display(), self.term)

    @models.permalink
    def get_absolute_url(self):
        return ('programme-detail', [], {'year_from': self.term.valid_from.year, \
                                         'year_to': self.term.valid_to.year, \
                                         'programme': self.order})


PROGRAMME_DEFAULT = {
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
        (RepresentativeVote.REPRESENTATIVE_VOTE_ABSTAIN, {
            'icon': 'icon-question-sign',
            'label': RepresentativeVote.REPRESENTATIVE_VOTE_LABELS[RepresentativeVote.REPRESENTATIVE_VOTE_ABSTAIN],
            'votes': 0,
            'votes_perc': 0,
            'representatives': []
        }),
        (RepresentativeVote.REPRESENTATIVE_VOTE_NOVOTE, {
            'icon': 'icon-remove-circle',
            'label': RepresentativeVote.REPRESENTATIVE_VOTE_LABELS[RepresentativeVote.REPRESENTATIVE_VOTE_NOVOTE],
            'votes': 0,
            'votes_perc': 0,
            'representatives': []
        }),
        (RepresentativeVote.REPRESENTATIVE_VOTE_MISSING, {
            'icon': 'icon-globe',
            'label': RepresentativeVote.REPRESENTATIVE_VOTE_LABELS[RepresentativeVote.REPRESENTATIVE_VOTE_MISSING],
            'votes': 0,
            'votes_perc': 0,
            'representatives': []
        })
    ])
}


NUMBERS_RE = re.compile(r'\d+')

class ProgrammeItem(models.Model):
    """
    Bod na programu jednani zastupitelstva.
    """
    PROGRAMME_YES = '+'
    PROGRAMME_NO  = '-'
    PROGRAMME_CONFUSED = '?'
    PROGRAMME_LABELS = {
        PROGRAMME_YES: u'Schváleno',
        PROGRAMME_NO: u'Neschváleno',
        PROGRAMME_CONFUSED: u'Zmatečné',
    }
    DECISION_LABELS = {
        PROGRAMME_YES: u'Přijatá',
        PROGRAMME_NO: u'Nepřijatá',
        PROGRAMME_CONFUSED: u'Nepřijatá',
    }
    PROGRAMME_ICONS = {
        PROGRAMME_YES: u'icon-thumbs-up',
        PROGRAMME_NO: u'icon-thumbs-down',
        PROGRAMME_CONFUSED: u'icon-question-sign',
    }
    PROGRAMME_CHOICES = (
        (PROGRAMME_YES, PROGRAMME_LABELS[PROGRAMME_YES]),
        (PROGRAMME_NO, PROGRAMME_LABELS[PROGRAMME_NO]),
        (PROGRAMME_CONFUSED, PROGRAMME_LABELS[PROGRAMME_CONFUSED]),
    )

    item             = models.CharField(u'Číslo bodu', max_length=10)
    title            = models.CharField(u'Titulek', max_length=2000)
    htitle           = models.CharField(u'Srozumitelný titulek', max_length=1000, blank=True, null=True)
    description_orig = models.TextField(u'Popis', blank=True, null=True)
    description      = models.TextField(editable=False, blank=True, null=True)
    programme        = models.ForeignKey(Programme, verbose_name=u"Program jednání zastupitelstva", related_name='items')
    # denormalizace
    ditem            = models.CharField(editable=False, max_length=30)
    created          = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated          = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Bod na programu jednání zastupitelstva'
        verbose_name_plural = u'Body z programu jednání zastupitelstva'
        ordering = ('ditem', )

    def __unicode__(self):
        return u'%s, bod %s' % (self.programme, self.item)

    @models.permalink
    def get_absolute_url(self):
        term = self.programme.term
        return ('programme-item-detail', [], {'year_from': term.valid_from.year, \
                                              'year_to': term.valid_to.year, \
                                              'programme': self.programme.order, \
                                              'item': self.item})

    def save(self, *args, **kwargs):
        self.description = typotexy(process_markdown(self.description_orig))
        self.ditem = self.denormalize_item()
        return super(ProgrammeItem, self).save(*args, **kwargs)

    def denormalize_item(self):
        """
        Prevadi atribut item (treba ve tvaru 1.2) do normalizovaneho tvaru
        (001-003).
        """
        orders = ["%03i" % int(i) for i in NUMBERS_RE.findall(self.item)]
        #orders.extend((5-len(orders))*["%03i" % 0])
        return '-'.join(orders)

    def get_next(self):
        qs = ProgrammeItem.objects.filter(programme=self.programme, \
                                          ditem__gt=self.ditem).order_by('ditem')
        return qs[0] if qs.exists() else None

    def get_prev(self):
        qs = ProgrammeItem.objects.filter(programme=self.programme, \
                                          ditem__lt=self.ditem).order_by('-ditem')
        return qs[0] if qs.exists() else None

    def get_voting_data(self):
        """
        Vrati SortedDict s prubehem hlasovani.
        """
        out = SortedDict()
        # rozprcani zastupitelu do slovniku
        for voting in self.voting.all().order_by('order'):
            counter = 0
            _item = deepcopy(PROGRAMME_DEFAULT)
            for rvote in voting.rvote.all().order_by('representative__person__last_name'):
                _item['data'][rvote.vote]['representatives'].append(rvote.representative)
                _item['data'][rvote.vote]['votes'] += 1
                counter += 1

            if counter == 0:
                continue
            _item['confused'] = voting.confused
            _item['description'] = voting.description
            _item['order'] = voting.order
            _item['decisions'] = voting.decisions.all()

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

        out = {'data': SortedDict()}
        for order in voting:
            if not voting[order] or not voting[order]['data']:
                continue
            item = voting[order]['data']

            total = sum([item[k]['votes'] for k in item])
            limit = int(math.ceil(total / 2.0))
            win = [k for k in item if item[k]['votes'] >= limit]
            if voting[order]['confused']:
                result = self.PROGRAMME_CONFUSED
            elif win and win[0] == RepresentativeVote.REPRESENTATIVE_VOTE_YES:
                result = self.PROGRAMME_YES
            else:
                result = self.PROGRAMME_NO

            out['data'][order] = {'result': result,
                                  'result_bool': result == self.PROGRAMME_YES,
                                  'limit': limit,
                                  'total': total,
                                  'tightly': result==self.PROGRAMME_YES and item[win[0]]['votes'] <= limit + 2,
                                  'icon': self.PROGRAMME_ICONS[result],
                                  'label': self.PROGRAMME_LABELS[result],
                                  'decision_label': self.DECISION_LABELS[result],
                                  'confused': voting[order]['confused'],
                                  'description': voting[order]['description'],
                                  'order': voting[order]['order']}

        # doplnime statisticke udaje o celkovych vysledcich
        out['confused_count'] = len([1 for k in out['data'] if out['data'][k]['confused']])
        out['total_count'] = len(out['data'])
        out['valid_count'] = out['total_count'] - out['confused_count']
        out['multiple_icon'] = 'icon-reorder'

        return out

    @staticmethod
    def normalize_item(item):
        out = replace_multiple_whitechars(item)
        return out.replace(' ', '').rstrip('.')

    @staticmethod
    def normalize_title(title):
        return replace_multiple_whitechars(title)


class ProgrammeHTitle(models.Model):
    """
    Navrhy srozumitelnych titulku k bodum programu.
    """
    htitle  = models.CharField(u'Srozumitelný titulek', max_length=1000)
    item    = models.ForeignKey(ProgrammeItem, verbose_name=u'Bod na programu jednání zastupitelstva', related_name='htitle_suggestions')
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
# TODO: vazba na navrhovatele

    class Meta:
        verbose_name = u'Návrh srozumitelného titulku'
        verbose_name_plural = u'Návrhy srozumitelných titulků'
        ordering = ('-created', )

    def __unicode__(self):
        return u'%s %s' % (self.htitle, self.item)


class ProgrammeHDescription(models.Model):
    """
    Navrhy obsahu bodu programu.
    """
    hdescription = models.TextField(u"Srozumitelný popis")
    item         = models.ForeignKey(ProgrammeItem, verbose_name=u'Bod na programu jednání zastupitelstva', related_name='hdescription_suggestions')
    created      = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated      = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
# TODO: vazba na navrhovatele

    class Meta:
        verbose_name = u'Návrh srozumitelného obsahu'
        verbose_name_plural = u'Návrhy srozumitelných obsahů'
        ordering = ('-created', )

    def __unicode__(self):
        return u'%s %s' % (self.hdescription[:20], self.item)


# --- usneseni ----------------------------------------------------------------

class Decision(models.Model):
    """
    Usneseni.
    """
    code             = models.CharField(u'Kód usnesení', max_length=10)
    title            = models.CharField(u'Titulek', max_length=2000)
    description_orig = models.TextField(u'Popis')
    description      = models.TextField(editable=False, blank=True, null=True)
    voting           = models.ForeignKey('voting.RepresentativeVoting', verbose_name=u"Hlasování k bodu programu", related_name='decisions')
    term             = models.CharField(u'Termín', max_length=50, default="Ihned", blank=True, null=True)
    responsibles     = models.ManyToManyField('authority.Person', verbose_name=u"Zodpovědné osoby", related_name="decisions", blank=True, null=True)
    created          = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated          = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Usnesení'
        verbose_name_plural = u'Usnesení'
        ordering = ('code', )

    def __unicode__(self):
        return u'%s %s' % (self.code, self.voting)

    def save(self, *args, **kwargs):
        self.description = typotexy(process_markdown(self.description_orig))
        return super(Decision, self).save(*args, **kwargs)

    @staticmethod
    def normalize_code(code):
        return replace_multiple_whitechars(code)

    @staticmethod
    def normalize_title(title):
        return replace_multiple_whitechars(title)
