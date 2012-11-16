# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.db import models

class PeriodQuerySet(models.query.QuerySet):
    def valid(self, date=None):
        if date is None:
            return self.filter(valid=True)
        else:
            return self.filter(models.Q(valid_from__lte=date, valid_to__gt=date) |\
                               models.Q(valid_from__lte=date, valid_to__isnull=True))

    def valid_interval(self, date_from, date_to):
        if date_to is None:
            return self.filter(valid_to__isnull=True)
        else:
            return self.filter(models.Q(valid_from__lt=date_from, valid_to__gte=date_from) |\
                               models.Q(valid_from__gte=date_from, valid_to__lte=date_to) |\
                               models.Q(valid_from__lte=date_to, valid_to__gt=date_to) |\
                               models.Q(valid_to__isnull=True))
