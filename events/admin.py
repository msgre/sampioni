# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import RepresentativeAgenda, RepresentativeAgendaItem

admin.site.register(RepresentativeAgenda)
admin.site.register(RepresentativeAgendaItem)
