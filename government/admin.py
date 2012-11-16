# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Party, Politician, Term, Representative

admin.site.register(Party)
admin.site.register(Politician)
admin.site.register(Term)
admin.site.register(Representative)
