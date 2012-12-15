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
    list_display = ('display_order', 'term', 'type', 'date')
    list_filter = ('term', 'type')

    def display_order(self, obj):
        return u'%s. zastupitelstvo' % obj.order
    display_order.short_description = u'Pořadové číslo'
    display_order.admin_order_field = 'order'


admin.site.register(Programme, ProgrammeAdmin)
