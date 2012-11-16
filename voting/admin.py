# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import RepresentativeVote, PublicVote

admin.site.register(RepresentativeVote)
admin.site.register(PublicVote)
