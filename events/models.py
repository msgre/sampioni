# -*- coding: utf-8 -*-

"""
Dulezite udalosti.

Momentalne pouze bod jednani zastupitelstva. V budoucnu mozna i body z jednani
rady, prip. dalsi verejne vystupy mesta (napr. Forum 2025, apod).
"""

from django.db import models


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
    term    = models.ForeignKey("government.Term", verbose_name=u"Volební období")
    date    = models.DateTimeField(u"Datum konání")
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Jednání zastupitelstva'
        verbose_name_plural = u'Jednání zastupitelstev'
        ordering = ('-term__valid_from', 'order')

    def __unicode__(self):
        return u'%s %s' % (self.order, self.get_type_display())


class RepresentativeAgendaItem(models.Model):
    """
    Bod na jednani zastupitelstva.
    """
    item    = models.CharField(u'Číslo bodu', max_length=10)
    title   = models.CharField(u'Titulek', max_length=1000)
    agenda  = models.ForeignKey(RepresentativeAgenda, verbose_name=u"Jednání zastupitelstva")
    date    = models.DateTimeField(u"Datum konání")
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Bod na jednání zastupitelstva'
        verbose_name_plural = u'Body z jednání zastupitelstva'
        ordering = ('-agenda__term__valid_from', 'item')

    def __unicode__(self):
        return u'%s %s' % (self.agenda, self.item)
