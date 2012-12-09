# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import RepresentativeVoting, RepresentativeVote, PublicVote


class RepresentativeVoteInline(admin.TabularInline):
    extra = 25
    model = RepresentativeVote

class RepresentativeVotingAdmin(admin.ModelAdmin):
    inlines = [
        RepresentativeVoteInline,
    ]


admin.site.register(RepresentativeVoting, RepresentativeVotingAdmin)
admin.site.register(PublicVote)
