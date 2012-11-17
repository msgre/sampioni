# -*- coding: utf-8 -*-

"""
TODO:
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class AttachmentCategory(models.Model):
    """
    Kategorie priloh.
    """
    title = models.CharField(u'Název', max_length=200)
    order = models.IntegerField(u'Pořadí', default=100)

    class Meta:
        verbose_name = u'Kategorie přílohy'
        verbose_name_plural = u'Kategorie příloh'
        ordering = ('order', )

    def __unicode__(self):
        return self.title


class Attachment(models.Model):
    """
    Priloha.
    """
    source      = models.CharField(u'Zdroj', max_length=200)
    url         = models.URLField(u'URL adresa zdroje', blank=True, null=True)
    description = models.TextField(u'Popis/Citace')
    category    = models.ForeignKey(AttachmentCategory, verbose_name=u'Kategorie')
    created     = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated     = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Příloha'
        verbose_name_plural = u'Přílohy'
        ordering = ('-created', )

    def __unicode__(self):
        return self.source


class AttachmentOrder(models.Model):
    """
    Poradi priloh v ramci kategorie.
    """
    attachment = models.ForeignKey(Attachment)
    comment    = models.ForeignKey('Comment')
    order      = models.IntegerField(u'Pořadí', default=100)

    class Meta:
        ordering = ('order', )


class Comment(models.Model):
    """
    Komentar k nejake udalosti z mesta.
    """
    title       = models.CharField(u'Titulek', max_length=1000)
    slug        = models.SlugField(u'Webové jméno')
    description = models.TextField(u'Komentář')
    attachments = models.ManyToManyField(Attachment, through='AttachmentOrder')
    created     = models.DateTimeField(u"Datum vytvoření", auto_now_add=True)
    updated     = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
    # obecna vazba na objekt, ktery je komentovany
    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = u'Komentář'
        verbose_name_plural = u'Komentáře'
        ordering = ('-created', )

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('comment-detail', [], {'slug': self.slug})
