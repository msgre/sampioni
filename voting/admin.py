# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin

from .models import RepresentativeVoting, RepresentativeVote, PublicVote
from .forms import RepresentativeVoteInlineForm, DecisionInlineForm
from municipal.models import Decision


class RepresentativeVoteInline(admin.TabularInline):
    extra = 25
    max_num = 25
    model = RepresentativeVote
    form = RepresentativeVoteInlineForm

class DecisionInline(admin.StackedInline):
    extra = 0
    model = Decision
    form = DecisionInlineForm

class RepresentativeVotingAdmin(admin.ModelAdmin):
    inlines = [
        DecisionInline,
        RepresentativeVoteInline,
    ]


admin.site.register(RepresentativeVoting, RepresentativeVotingAdmin)
admin.site.register(PublicVote)
