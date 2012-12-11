# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms

from .models import Programme, ProgrammeItem, Decision


class ProgrammeItemInline(admin.TabularInline):
    extra = 40
    model = ProgrammeItem
    fields = ('item', 'title')

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Titulek jako textarea (bo ti urednici nemaji soudnost).
        """
        if db_field.name == 'title':
            return forms.CharField(label=db_field.verbose_name, widget=forms.Textarea(attrs={'rows': '4', 'style': 'width:90%'}))
        return super(ProgrammeItemInline, self).formfield_for_dbfield(db_field, **kwargs)


class ProgrammeAdmin(admin.ModelAdmin):
    inlines = [
        ProgrammeItemInline,
    ]


admin.site.register(Programme, ProgrammeAdmin)
