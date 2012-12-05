# -*- coding: utf-8 -*-

"""
Hlasovani k bodum z jednani zastupitelstva.
"""

from django.db import models


class RepresentativeVote(models.Model):
    """
    Hlasovani zastupitele u konkretniho bodu jednani zastupitelstva.
    """
    REPRESENTATIVE_VOTE_YES     = u'+'
    REPRESENTATIVE_VOTE_NO      = u'-'
    REPRESENTATIVE_VOTE_NOTHING = u'0'
    REPRESENTATIVE_VOTE_MISSING = u'X'
    REPRESENTATIVE_VOTE_LABELS = {
        REPRESENTATIVE_VOTE_YES: u'Pro',
        REPRESENTATIVE_VOTE_NO: u'Proti',
        REPRESENTATIVE_VOTE_NOTHING: u'Zdržel se',
        REPRESENTATIVE_VOTE_MISSING: u'Nehlasoval',
    }
    REPRESENTATIVE_VOTE_CHOICES = (
        (REPRESENTATIVE_VOTE_YES, REPRESENTATIVE_VOTE_LABELS[REPRESENTATIVE_VOTE_YES]),
        (REPRESENTATIVE_VOTE_NO, REPRESENTATIVE_VOTE_LABELS[REPRESENTATIVE_VOTE_NO]),
        (REPRESENTATIVE_VOTE_NOTHING, REPRESENTATIVE_VOTE_LABELS[REPRESENTATIVE_VOTE_NOTHING]),
        (REPRESENTATIVE_VOTE_MISSING, REPRESENTATIVE_VOTE_LABELS[REPRESENTATIVE_VOTE_MISSING]),
    )

    representative = models.ForeignKey("authority.Representative", verbose_name=u'Zastupitel')
    item           = models.ForeignKey("events.RepresentativeAgendaItem", verbose_name=u'Bod na jednání zastupitelstva', related_name='rvotes')
    vote           = models.CharField(u'Hlas', max_length=1, choices=REPRESENTATIVE_VOTE_CHOICES)
    created        = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated        = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
    # denormalizace
    dparty_short           = models.CharField(max_length=15, editable=False)
    dpolitician_first_name = models.CharField(max_length=20, editable=False)
    dpolitician_last_name  = models.CharField(max_length=40, editable=False)

    class Meta:
        verbose_name = u'Hlas zastupitele'
        verbose_name_plural = u'Hlasy zastupitelů'
        ordering = ('-item__agenda__term__valid_from', 'dparty_short', 'dpolitician_last_name', )

    def __unicode__(self):
        return u'%s %s: %s' % (self.dpolitician_first_name, self.dpolitician_last_name, \
                               self.get_vote_display())

    def save(self, *args, **kwargs):
        self.dparty_short = self.representative.dparty_short
        self.dpolitician_first_name = self.representative.dpolitician_first_name
        self.dpolitician_last_name = self.representative.dpolitician_last_name
        return super(RepresentativeVote, self).save(*args, **kwargs)

class PublicVote(models.Model):
    """
    Hlasovani verejnosti ke konkretniho bodu jednani zastupitelstva.
    """
    PUBLIC_VOTE_YES     = u'+'
    PUBLIC_VOTE_NO      = u'-'
    PUBLIC_VOTE_CHOICES = (
        (PUBLIC_VOTE_YES, u'Pro'),
        (PUBLIC_VOTE_NO, u'Proti'),
    )

    ip      = models.GenericIPAddressField("IP adresa", blank=True, null=True)
    item    = models.ForeignKey("events.RepresentativeAgendaItem", verbose_name=u'Bod na jednání zastupitelstva', related_name='pvotes')
    vote    = models.CharField(u'Hlas', max_length=1, choices=PUBLIC_VOTE_CHOICES)
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Hlas lidu'
        verbose_name_plural = u'Hlasy lidu'
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s: %s' % (self.created, self.get_vote_display())
