# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import RepresentativeVoting, RepresentativeVote, PublicVote

admin.site.register(RepresentativeVoting)
admin.site.register(RepresentativeVote)
admin.site.register(PublicVote)
