# -*- coding: utf-8 -*-

"""
Hlasovani k bodum z jednani zastupitelstva.
"""

from django.db import models


class RepresentativeVoting(models.Model):
    """
    Hlasovani ke konkretnimu bodu na jednani.

    Poznamka: puvodne jsem si myslel, ze co bod jednani, to jedno hlasovani.
    Omyl! Je to pekny chaos. Nekdy se o temze bodu hlasuje vicekrat (prvni
    hlasovani se prohlasi za zmatecne), nekdy se hlasuje o kazdem podbode
    bodu zvlast, nekdy se v ramci bodu objevi protinavrh a hlasuje se
    o puvodnim zneni i o protinarhu, ... Variant je asi nekonecno.

    Proto je treba mit mezi konkretnim bode a hlasem zastupitele tento
    model.
    """
    item        = models.ForeignKey("municipal.ProgrammeItem", verbose_name=u'Bod na jednání zastupitelstva', related_name='voting')
    order       = models.IntegerField(u"Číslo hlasování", default=1)
    description = models.TextField(u"Popis hlasování", blank=True, null=True, help_text=u'Pokud se k bodu hlasuje vícekrát, je třeba jednotlivé hlasování od sebe odlišit nějakým popisem o co šlo.')
    confused    = models.BooleanField(u"Zmatečné hlasování", default=False, help_text=u'Někdy se o hlasování prohlásí, že bylo zmatečné. Byl to tento případ?')
    created     = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated     = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Hlasování zastupitelů k bodu'
        verbose_name_plural = u'Hlasování zastupitelů k bodům'
        ordering = ('-created', )
        unique_together = ('item', 'order')

    def __unicode__(self):
        description = self.description and self.description[:15] or u''
        return u'%s / %s' % (self.order, self.item)


class RepresentativeVote(models.Model):
    """
    Hlas zastupitele u konkretniho hlasovani.
    """
    REPRESENTATIVE_VOTE_YES     = u'+'
    REPRESENTATIVE_VOTE_NO      = u'-'
    REPRESENTATIVE_VOTE_ABSTAIN = u'0'
    REPRESENTATIVE_VOTE_NOVOTE  = u'X'
    REPRESENTATIVE_VOTE_MISSING = u'.'
    REPRESENTATIVE_VOTE_LABELS = {
        REPRESENTATIVE_VOTE_YES: u'Pro',
        REPRESENTATIVE_VOTE_NO: u'Proti',
        REPRESENTATIVE_VOTE_ABSTAIN: u'Zdržel se',
        REPRESENTATIVE_VOTE_NOVOTE: u'Nehlasoval',
        REPRESENTATIVE_VOTE_MISSING: u'Nepřítomen',
    }
    REPRESENTATIVE_VOTE_CHOICES = (
        (REPRESENTATIVE_VOTE_YES, REPRESENTATIVE_VOTE_LABELS[REPRESENTATIVE_VOTE_YES]),
        (REPRESENTATIVE_VOTE_NO, REPRESENTATIVE_VOTE_LABELS[REPRESENTATIVE_VOTE_NO]),
        (REPRESENTATIVE_VOTE_ABSTAIN, REPRESENTATIVE_VOTE_LABELS[REPRESENTATIVE_VOTE_ABSTAIN]),
        (REPRESENTATIVE_VOTE_NOVOTE, REPRESENTATIVE_VOTE_LABELS[REPRESENTATIVE_VOTE_NOVOTE]),
        (REPRESENTATIVE_VOTE_MISSING, REPRESENTATIVE_VOTE_LABELS[REPRESENTATIVE_VOTE_MISSING]),
    )

    representative = models.ForeignKey("authority.Representative", verbose_name=u'Zastupitel')
    voting         = models.ForeignKey(RepresentativeVoting, verbose_name=u'Hlasování na jednání zastupitelstva', related_name='rvote')
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
        ordering = ('-created', )
        unique_together = ('representative', 'voting')

    def __unicode__(self):
        return u'%s %s: %s' % (self.dpolitician_first_name, self.dpolitician_last_name, \
                               self.get_vote_display())

    def save(self, *args, **kwargs):
        self.dparty_short = self.representative.dparty_short
        self.dpolitician_first_name = self.representative.dpolitician_first_name
        self.dpolitician_last_name = self.representative.dpolitician_last_name
        return super(RepresentativeVote, self).save(*args, **kwargs)

    @staticmethod
    def parse(data):
        """
        TODO:
        """
        data = data.strip().lower()
        for k, v in RepresentativeVote.REPRESENTATIVE_VOTE_LABELS.iteritems():
            if v.lower() == data:
                return k
        return None


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
    item    = models.ForeignKey("municipal.ProgrammeItem", verbose_name=u'Bod na jednání zastupitelstva', related_name='pvotes')
    vote    = models.CharField(u'Hlas', max_length=1, choices=PUBLIC_VOTE_CHOICES)
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Hlas veřejnosti'
        verbose_name_plural = u'Hlasy veřejnosti'
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s: %s' % (self.created, self.get_vote_display())
