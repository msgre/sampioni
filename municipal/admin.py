# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Programme, ProgrammeItem, Decision

admin.site.register(Programme)
admin.site.register(ProgrammeItem)
admin.site.register(Decision)
