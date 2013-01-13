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


class Person(models.Model):
    """
    Clovek.
    """
    first_name = models.CharField(u'Jméno', max_length=20)
    last_name  = models.CharField(u'Příjmení', max_length=40)
    photo      = models.ImageField(upload_to='photos', blank=True, null=True)
    created    = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated    = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Člověk'
        verbose_name_plural = u'Lidé'
        ordering = ('last_name', )

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class PersonSynonym(models.Model):
    """
    Alternativni pojmenovani cloveka.
    """
    nick   = models.CharField(u'Synonymum', max_length=100)
    person = models.ForeignKey(Person, verbose_name=u'Člověk', related_name='synonymous', null=True, blank=True)

    class Meta:
        verbose_name = u'Alt. jméno člověka'
        verbose_name_plural = u'Alt. jména člověka'
        ordering = ('person', 'nick', )

    def __unicode__(self):
        return u'%s: %s' % (self.nick, self.person)


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
    party   = models.ForeignKey(Party, verbose_name=u'Strana')
    person  = models.ForeignKey(Person, verbose_name=u'Člověk', related_name='representatives')
    term    = models.ForeignKey(Term, verbose_name=u'Volební období')
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
    # denormalizace
    dparty_short           = models.CharField(max_length=15, editable=False)
    dpolitician_first_name = models.CharField(max_length=20, editable=False)
    dpolitician_last_name  = models.CharField(max_length=40, editable=False)

    class Meta:
        verbose_name = u'Zastupitel'
        verbose_name_plural = u'Zastupitelé'
        ordering = ('dpolitician_last_name', '-valid_from')

    def __unicode__(self):
        return unicode(self.person)

    def save(self, *args, **kwargs):
        self.dparty_short = self.party.short
        self.dpolitician_first_name = self.person.first_name
        self.dpolitician_last_name = self.person.last_name
        return super(Representative, self).save(*args, **kwargs)

    def get_full_name(self):
        return u'%s %s' % (self.dpolitician_first_name, self.dpolitician_last_name)
