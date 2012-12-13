# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms

from .models import Programme, ProgrammeItem, Decision
from .forms import ProgrammeItemInlineForm


class ProgrammeItemInline(admin.TabularInline):
    extra = 40
    model = ProgrammeItem
    form = ProgrammeItemInlineForm

class ProgrammeAdmin(admin.ModelAdmin):
    inlines = [
        ProgrammeItemInline,
    ]


admin.site.register(Programme, ProgrammeAdmin)
