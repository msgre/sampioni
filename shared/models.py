# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.db import models

from model_utils.managers import PassThroughManager

from .managers import PeriodQuerySet


class PeriodModel(models.Model):
    """
    Abstraktni model pro vyjadreni obdobi od-do.
    """
    valid_from = models.DateTimeField(u"Platné od")
    valid_to   = models.DateTimeField(u"Platné do", blank=True, null=True)
    # denormalizace
    valid      = models.BooleanField(u"Aktuálně platný záznam", default=True, editable=False)
    objects    = PassThroughManager(PeriodQuerySet)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.valid = self.valid_to is None
        super(PeriodModel, self).save(*args, **kwargs)
