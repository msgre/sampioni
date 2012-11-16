# -*- coding: utf-8 -*-

"""
Urad -- struktury popisujici volebni obdobi, politiky a zastupitele.
"""

from django.db import models

from shared.models import PeriodModel


class Party(models.Model):
    """
    Politicka strana.
    """
    title   = models.CharField(u'Název', max_length=50)
    short   = models.CharField(u'Zkratka', max_length=15, unique=True)
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Politická strana'
        verbose_name_plural = u'Politické strany'
        ordering = ('short', )

    def __unicode__(self):
        return self.short


class Politician(models.Model):
    """
    Politik.
    """
    first_name = models.CharField(u'Jméno', max_length=20)
    last_name  = models.CharField(u'Příjmení', max_length=40)
    # TODO: fotka
    created    = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated    = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Politik'
        verbose_name_plural = u'Politici'
        ordering = ('last_name', )

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class Term(PeriodModel):
    """
    Volebni obdobi.
    """
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Volební období'
        verbose_name_plural = u'Volební období'
        ordering = ('-valid_from', )

    def __unicode__(self):
        return u'%s-%s' % (self.valid_from.year, self.valid_to.year)


class Representative(PeriodModel):
    """
    Zastupitel.
    """
    party      = models.ForeignKey(Party, verbose_name=u'Strana')
    politician = models.ForeignKey(Politician, verbose_name=u'Politik')
    term       = models.ForeignKey(Term, verbose_name=u'Volební období')
    created    = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated    = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
    # denormalizace
    dparty_short           = models.CharField(max_length=15, editable=False)
    dpolitician_first_name = models.CharField(max_length=20, editable=False)
    dpolitician_last_name  = models.CharField(max_length=40, editable=False)

    class Meta:
        verbose_name = u'Zastupitel'
        verbose_name_plural = u'Zastupitelé'
        ordering = ('dpolitician_last_name', '-valid_from')

    def __unicode__(self):
        return unicode(self.politician)

    def save(self, *args, **kwargs):
        self.dparty_short = self.party.short
        self.dpolitician_first_name = self.politician.first_name
        self.dpolitician_last_name = self.politician.last_name
        return super(Representative, self).save(*args, **kwargs)
